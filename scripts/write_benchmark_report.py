import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tomllib
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
    "pyqubo",
    "qiskit",
    "qiskit-optimization",
    "qubovert",
    "scienceplots",
    "scipy",
]

JULIA_PACKAGES = [
    "CSV",
    "JuMP",
    "QUBOTools",
    "ToQUBO",
]


def package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def read_julia_manifest():
    manifest_path = BENCHMARK / "ToQUBO" / "Manifest.toml"
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


def csv_summary(path):
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    times = [float(row["time"]) for row in rows]
    nvars = [int(row["nvar"]) for row in rows]

    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(rows),
        "max_nvar": max(nvars),
        "max_time": max(times),
    }


def result_files():
    files = []
    for path in sorted(BENCHMARK.glob("*/results.*.csv")):
        files.append(csv_summary(path))
    return files


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
            "ToQUBO v0.4.1 does not define ToQUBO.qubo; the benchmark still "
            "reaches the QUBOTools backend through JuMP/ToQUBO optimizer internals."
        ),
        "largest_tsp_nvar": int(largest["nvar"]),
        "largest_tsp_total_time": total_time,
    }

    if "convert_time" in fieldnames:
        convert_time = float(largest["convert_time"])
        summary.update(
            {
                "status": "internal-backend-access",
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


def main():
    DATA.mkdir(exist_ok=True)
    julia_manifest = read_julia_manifest()
    julia = julia_runtime()

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "result_set": {
            "id": os.environ.get("BENCHMARK_RESULT_SET_ID", "latest-stack-2026-06-19-rerun"),
            "status": os.environ.get("BENCHMARK_RESULT_STATUS", "coherent-diagnostic-rerun"),
            "supersedes": "mixed-date latest-stack experiment from PR #11",
            "closes_issue": None,
            "refs_issue": 12,
            "openqaoa": {
                "status": "excluded",
                "reason": (
                    "openqaoa==0.2.6 remains behind a Python version marker because "
                    "it does not resolve on the Python 3.12 runtime used here."
                ),
            },
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
        },
        "packages": {
            "python": {name: package_version(name) for name in PYTHON_PACKAGES},
            "julia": julia_manifest["packages"],
        },
        "toqubo_extraction": toqubo_extraction_summary(),
        "files": result_files(),
    }

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
