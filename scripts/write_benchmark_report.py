import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark"
DATA = ROOT / "data"
REPORT = DATA / "report.json"

PYTHON_PACKAGES = [
    "amplify",
    "dimod",
    "docplex",
    "matplotlib",
    "numpy",
    "openqaoa",
    "mitiq",
    "pyqubo",
    "qiskit",
    "qiskit-optimization",
    "qubovert",
    "scienceplots",
    "scipy",
]

PYTHON_REQUIREMENT_FILES = [
    BENCHMARK / "amplify" / "requirements.txt",
    BENCHMARK / "dwave" / "requirements.txt",
    BENCHMARK / "openqaoa" / "requirements.txt",
    BENCHMARK / "pyqubo" / "requirements.txt",
    BENCHMARK / "qiskit" / "requirements.txt",
    BENCHMARK / "qubovert" / "requirements.txt",
    ROOT / "plot" / "requirements.txt",
]

JULIA_PACKAGES = [
    "CSV",
    "JuMP",
    "QUBOTools",
    "ToQUBO",
]

PHASE_SPLIT_COLUMNS = [
    "jump_time",
    "toqubo_time",
    "model_time",
    "compiler_time",
    "convert_time",
]

PACKAGE_PHASE_SPLIT_SUPPORT = {
    "ToQUBO": ["jump_time", "toqubo_time", "compiler_time", "convert_time"],
    "amplify": ["model_time", "convert_time"],
    "dwave": ["model_time", "compiler_time", "convert_time"],
    "openqaoa": ["model_time", "compiler_time", "convert_time"],
    "pyqubo": ["model_time", "compiler_time", "convert_time"],
    "qiskit": ["model_time", "compiler_time", "convert_time"],
    "qubovert": ["model_time", "convert_time"],
}


def pinned_requirement_version(name):
    normalized_name = name.lower()

    for path in PYTHON_REQUIREMENT_FILES:
        for line in path.read_text(encoding="utf-8").splitlines():
            requirement = line.strip()

            if not requirement or requirement.startswith("#") or ";" in requirement:
                continue

            package, separator, version = requirement.partition("==")

            if separator and package.lower() == normalized_name:
                return version

    return None


def package_version(name):
    pinned_version = pinned_requirement_version(name)

    if pinned_version is not None:
        return pinned_version

    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def read_julia_manifest():
    manifest_path = Path(
        os.environ.get(
            "BENCHMARK_TOQUBO_MANIFEST",
            BENCHMARK / "ToQUBO" / "Manifest.toml",
        )
    )
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    deps = manifest.get("deps", {})

    packages = {}
    for name in JULIA_PACKAGES:
        entries = deps.get(name, [])
        if isinstance(entries, dict):
            entries = [entries]
        version = None
        if entries:
            version = entries[0].get("version")
        packages[name] = version

    return {
        "path": str(manifest_path),
        "julia": manifest.get("julia_version"),
        "packages": packages,
    }


def julia_runtime():
    executable = os.environ.get("BENCHMARK_JULIA", "julia")
    version = os.environ.get("BENCHMARK_JULIA_VERSION")

    if version is None:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout

    return {
        "executable": executable,
        "version": version.strip(),
    }


def cpu_model():
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor()


def package_name(path):
    return path.relative_to(BENCHMARK).parts[0]


def problem_name(path):
    parts = path.name.split(".")

    if len(parts) >= 3 and parts[0] == "results":
        return parts[1]

    return path.stem


def _float_equal(left, right):
    return abs(float(left) - float(right)) <= 1e-12


def _column_matches(rows, column, reference="time"):
    if not rows:
        return False

    return all(_float_equal(row[reference], row[column]) for row in rows)


def sampling_metadata(rows, fieldnames):
    fieldnames = set(fieldnames or [])

    if "sample_count" not in fieldnames:
        return {
            "time_statistic": "single_sample",
            "sample_count": 1,
            "warmup_count": 0,
        }

    sample_counts = sorted({int(float(row["sample_count"])) for row in rows})
    warmup_counts = sorted({int(float(row.get("warmup_count", 0))) for row in rows})
    statistic = "custom"

    for name in ("min", "median", "mean"):
        column = f"time_{name}"

        if column in fieldnames and _column_matches(rows, column):
            statistic = name
            break

    return {
        "time_statistic": statistic,
        "sample_count": sample_counts[0] if len(sample_counts) == 1 else sample_counts,
        "warmup_count": warmup_counts[0] if len(warmup_counts) == 1 else warmup_counts,
    }


def phase_split_metadata(path, fieldnames):
    package = package_name(path)
    fieldnames = set(fieldnames or [])
    recorded_columns = [
        column for column in PHASE_SPLIT_COLUMNS
        if column in fieldnames
    ]
    supported_columns = PACKAGE_PHASE_SPLIT_SUPPORT.get(package, [])

    if recorded_columns:
        status = "recorded"
    elif supported_columns:
        status = "supported-not-recorded"
    else:
        status = "not-available"

    return {
        "status": status,
        "recorded_columns": recorded_columns,
        "supported_columns": supported_columns,
    }


def csv_summary(path):
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    times = [float(row["time"]) for row in rows]
    nvars = [int(row["nvar"]) for row in rows]
    sampling = sampling_metadata(rows, fieldnames)

    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(rows),
        "max_nvar": max(nvars),
        "max_time": max(times),
        "time_statistic": sampling["time_statistic"],
        "sample_count": sampling["sample_count"],
        "warmup_count": sampling["warmup_count"],
        "phase_splits": phase_split_metadata(path, fieldnames),
    }


def result_files():
    files = []
    for path in sorted(BENCHMARK.glob("*/results.*.csv")):
        files.append(csv_summary(path))
    return files


def _summary_value(values):
    values = list(values)

    if len(values) == 1:
        return values[0]

    return sorted(values, key=lambda value: json.dumps(value, sort_keys=True))


def benchmark_methodology(files):
    time_statistics = {entry["time_statistic"] for entry in files}
    sample_counts = {json.dumps(entry["sample_count"], sort_keys=True) for entry in files}
    warmup_counts = {json.dumps(entry["warmup_count"], sort_keys=True) for entry in files}

    return {
        "time_column": "Summary statistic used by existing plots.",
        "time_statistic": _summary_value(time_statistics),
        "sample_count": _summary_value(json.loads(value) for value in sample_counts),
        "warmup_count": _summary_value(json.loads(value) for value in warmup_counts),
        "raw_samples": "Not stored in the compact live CSV files.",
    }


def phase_split_availability(files):
    availability = {}

    for entry in files:
        path = BENCHMARK / Path(entry["path"]).relative_to("benchmark")
        package = package_name(path)
        problem = problem_name(path)

        availability.setdefault(package, {})[problem] = entry["phase_splits"]

    return availability


def toqubo_extraction_summary(path=None):
    if path is None:
        path = BENCHMARK / "ToQUBO" / "results.tsp.csv"
    else:
        path = Path(path)

    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        fieldnames = set(reader.fieldnames or [])

    largest = max(rows, key=lambda row: int(row["nvar"]))
    total_time = float(largest["time"])

    summary = {
        "implementation": "benchmark/ToQUBO/problems.jl:extract_qubo_backend",
        "public_api_check": (
            "The benchmark uses the supported QUBOTools.backend(model) path "
            "added for ToQUBO-compiled JuMP models."
        ),
        "largest_tsp_nvar": int(largest["nvar"]),
        "largest_tsp_total_time": total_time,
    }

    if "convert_time" in fieldnames:
        convert_time = float(largest["convert_time"])
        summary.update(
            {
                "status": "public-backend-api",
                "largest_tsp_convert_time": convert_time,
                "largest_tsp_convert_share": convert_time / total_time,
            }
        )
    elif "toqubo_time" in fieldnames:
        summary.update(
            {
                "status": "phase-split-unavailable",
                "reason": "ToQUBO result CSV does not include convert_time.",
                "largest_tsp_toqubo_time": float(largest["toqubo_time"]),
            }
        )
    else:
        summary.update(
            {
                "status": "extraction-unavailable",
                "reason": "ToQUBO result CSV does not include convert_time or toqubo_time.",
            }
        )

    return summary


def toqubo_dependency_context():
    values = {
        "status": os.environ.get("BENCHMARK_TOQUBO_DEPENDENCY_STATUS"),
        "toqubo": os.environ.get("BENCHMARK_TOQUBO_SOURCE"),
        "qubotools": os.environ.get("BENCHMARK_QUBOTOOLS_SOURCE"),
        "note": os.environ.get("BENCHMARK_TOQUBO_DEPENDENCY_NOTE"),
    }

    context = {key: value for key, value in values.items() if value}

    if context:
        return context

    return {
        "status": "registered-manifest",
        "note": "Julia package sources come from benchmark/ToQUBO/Manifest.toml.",
    }


def openqaoa_context():
    version = package_version("openqaoa")

    if version:
        context = {
            "status": "included",
            "version": version,
            "note": (
                "OpenQAOA runs in an isolated Python 3.10 venv because "
                "openqaoa==0.2.6 depends on an old Qiskit plugin stack while "
                "the Qiskit benchmark uses qiskit==2.4.2."
            ),
        }

        runtime = os.environ.get("BENCHMARK_OPENQAOA_PYTHON")
        runtime_version = os.environ.get("BENCHMARK_OPENQAOA_PYTHON_VERSION")

        if runtime:
            context["python_executable"] = runtime
        if runtime_version:
            context["python"] = runtime_version

        return context

    return {
        "status": "excluded",
        "reason": (
            "openqaoa==0.2.6 remains behind a Python version marker because "
            "it does not resolve on the current Python runtime used here."
        ),
    }


def main():
    DATA.mkdir(exist_ok=True)
    julia_manifest = read_julia_manifest()
    julia = julia_runtime()
    files = result_files()

    report = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "result_set": {
            "id": os.environ.get("BENCHMARK_RESULT_SET_ID", "latest-stack-2026-06-19-rerun"),
            "status": os.environ.get("BENCHMARK_RESULT_STATUS", "coherent-diagnostic-rerun"),
            "supersedes": "mixed-date latest-stack experiment from PR #11",
            "closes_issue": None,
            "refs_issue": 12,
            "openqaoa": openqaoa_context(),
            "toqubo_dependencies": toqubo_dependency_context(),
        },
        "environment": {
            "os": platform.platform(),
            "machine": platform.machine(),
            "cpu": cpu_model(),
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "julia": julia["version"],
            "julia_executable": julia["executable"],
            "julia_manifest": julia_manifest["julia"],
            "julia_manifest_path": julia_manifest["path"],
        },
        "packages": {
            "python": {name: package_version(name) for name in PYTHON_PACKAGES},
            "julia": julia_manifest["packages"],
        },
        "benchmark_methodology": benchmark_methodology(files),
        "phase_split_availability": phase_split_availability(files),
        "toqubo_extraction": toqubo_extraction_summary(),
        "files": files,
    }

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
