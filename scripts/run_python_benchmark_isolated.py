import csv
import gc
import multiprocessing
import os
from pathlib import Path
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark import (  # noqa: E402
    _fieldnames,
    collect_samples,
    npp_data,
    npp_nvar,
    report,
    sample_count,
    summarize_samples,
    time_statistic,
    tsp_data,
    tsp_nvar,
    warmup_count,
)


PACKAGES = {
    "amplify": "benchmark.amplify.__main__",
    "dwave": "benchmark.dwave.__main__",
    "openqaoa": "benchmark.openqaoa.__main__",
    "pyqubo": "benchmark.pyqubo.__main__",
    "qiskit": "benchmark.qiskit.__main__",
    "qubovert": "benchmark.qubovert.__main__",
}

PROBLEMS = {
    "tsp": {
        "data": tsp_data,
        "nvar": tsp_nvar,
        "start": 5,
        "step": 5,
        "stop": 100,
        "time_limit": 100.0,
    },
    "npp": {
        "data": npp_data,
        "nvar": npp_nvar,
        "start": 20,
        "step": 20,
        "stop": 1000,
        "time_limit": 5.0,
    },
}


def import_run_function(module_name, problem):
    module = __import__(module_name, fromlist=[problem])

    return getattr(module, problem)


def child_run(queue, run, n, data_value):
    try:
        queue.put(("ok", run(n, data_value)))
    except BaseException:
        queue.put(("error", traceback.format_exc()))


def isolated_run(run, n, data_value):
    context = multiprocessing.get_context(
        os.environ.get("BENCHMARK_MULTIPROCESS_CONTEXT", "fork")
    )
    queue = context.Queue()
    process = context.Process(target=child_run, args=(queue, run, n, data_value))
    process.start()
    process.join()

    try:
        status, payload = queue.get_nowait()
    except Exception:
        status = "error"
        payload = f"child process exited with status {process.exitcode}"

    queue.close()
    queue.join_thread()

    if status == "ok" and process.exitcode == 0:
        return payload

    if status == "error" and process.exitcode == 0:
        raise RuntimeError(payload)

    raise RuntimeError(
        f"child process exited with status {process.exitcode}\n{payload}"
    )


def configured_rows(path, samples_run, warmups_run):
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        fieldnames = set(reader.fieldnames or [])

    if not {"sample_count", "warmup_count"} <= fieldnames:
        return []

    if any(
        int(float(row["sample_count"])) != samples_run
        or int(float(row["warmup_count"])) != warmups_run
        for row in rows
    ):
        return []

    return rows


def coerce_row(row):
    coerced = {"nvar": int(float(row["nvar"]))}

    for key, value in row.items():
        if key == "nvar":
            continue
        if value == "":
            coerced[key] = ""
        else:
            coerced[key] = float(value)

    return coerced


def write_rows(path, rows):
    fields = _fieldnames(rows)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()

        for row in sorted(rows, key=lambda value: int(value["nvar"])):
            writer.writerow({field: row.get(field, "") for field in fields})


def row_time(row):
    return float(row["time"])


def trim_after_threshold(rows, time_limit):
    trimmed = []

    for row in sorted(rows, key=lambda value: int(value["nvar"])):
        trimmed.append(row)

        if row_time(row) > time_limit:
            break

    return trimmed


def benchmark_problem(package, module_name, problem, config):
    samples_run = sample_count()
    warmups_run = warmup_count()
    selected_statistic = time_statistic()
    output_path = ROOT / "benchmark" / package / f"results.{problem}.csv"
    rows = [coerce_row(row) for row in configured_rows(output_path, samples_run, warmups_run)]
    trimmed_rows = trim_after_threshold(rows, config["time_limit"])

    if len(trimmed_rows) != len(rows):
        rows = trimmed_rows
        write_rows(output_path, rows)

    completed_rows = {int(row["nvar"]): row for row in rows}
    run = import_run_function(module_name, problem)

    def run_isolated(n, data_value):
        return isolated_run(run, n, data_value)

    print(f"Problem: {problem}", flush=True)

    for n in range(config["start"], config["stop"] + config["step"], config["step"]):
        nvar = config["nvar"](n)

        completed_row = completed_rows.get(nvar)

        if completed_row is not None:
            if row_time(completed_row) > config["time_limit"]:
                break
            continue

        data_value = config["data"](n)
        samples_data = collect_samples(
            run_isolated,
            n,
            data_value,
            samples_run=samples_run,
            warmups_run=warmups_run,
        )

        time_info = summarize_samples(
            samples_data,
            samples_run=samples_run,
            warmups_run=warmups_run,
            statistic=selected_statistic,
        )

        report(n, nvar, **time_info)

        row = {"nvar": nvar, **time_info}
        rows.append(row)
        completed_rows[nvar] = row
        write_rows(output_path, rows)
        gc.collect()

        if time_info["total_time"] > config["time_limit"]:
            break


def main(argv):
    packages = argv[1:] or sorted(PACKAGES)

    for package in packages:
        if package not in PACKAGES:
            raise SystemExit(f"unknown package: {package}")

        print(f"Running {package} with isolated samples...", flush=True)
        module_name = PACKAGES[package]

        for problem, config in PROBLEMS.items():
            benchmark_problem(package, module_name, problem, config)


if __name__ == "__main__":
    main(sys.argv)
