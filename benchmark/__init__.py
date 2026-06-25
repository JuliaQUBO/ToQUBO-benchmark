# Standard Library
import csv
import gc
import os
from pathlib import Path
import statistics

SUMMARY_STATISTICS = ("min", "median", "mean", "std")
PHASE_COLUMNS = ("model_time", "compiler_time", "convert_time")


def _env_int(name: str, default: int, minimum: int) -> int:
    raw_value = os.environ.get(name)

    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw_value!r}") from exc

    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {value}")

    return value


def sample_count() -> int:
    return _env_int("BENCHMARK_SAMPLES", 1, 1)


def warmup_count() -> int:
    return _env_int("BENCHMARK_WARMUPS", 1, 0)


def time_statistic() -> str:
    statistic = os.environ.get("BENCHMARK_TIME_STATISTIC", "min").strip().lower()

    if statistic not in {"min", "median", "mean"}:
        raise ValueError(
            "BENCHMARK_TIME_STATISTIC must be one of: min, median, mean"
        )

    return statistic


def _population_std(values):
    if len(values) <= 1:
        return 0.0

    return statistics.pstdev(values)


def _summary(values):
    return {
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "std": _population_std(values),
    }


def summarize_samples(samples, *, samples_run: int, warmups_run: int, statistic: str):
    if not samples:
        raise ValueError("at least one benchmark sample is required")
    if statistic not in {"min", "median", "mean"}:
        raise ValueError(f"unsupported time statistic: {statistic}")

    metrics = sorted({key for sample in samples for key in sample})

    if "total_time" not in metrics:
        raise KeyError("benchmark samples must include total_time")

    summary = {
        "sample_count": samples_run,
        "warmup_count": warmups_run,
    }

    for metric in metrics:
        values = [float(sample[metric]) for sample in samples if metric in sample]
        stats = _summary(values)

        summary[metric] = stats[statistic]

        for name in SUMMARY_STATISTICS:
            summary[f"{metric}_{name}"] = stats[name]

    summary["time"] = summary["total_time"]

    for name in SUMMARY_STATISTICS:
        summary[f"time_{name}"] = summary[f"total_time_{name}"]

    return summary


def _run_once(run, n, data_value):
    gc.collect()
    gc.disable()

    try:
        return run(n, data_value)
    finally:
        gc.enable()


def collect_samples(run, n, data_value, *, samples_run: int, warmups_run: int):
    for _ in range(warmups_run):
        _run_once(run, n, data_value)

    return [_run_once(run, n, data_value) for _ in range(samples_run)]

def tsp_data(n: int):
    import numpy as np

    return np.array([[abs(i - j) for j in range(n)] for i in range(n)])

def tsp_nvar(n: int):
    return n * n

def npp_data(n: int):
    import numpy as np

    return np.array([k for k in range(1, n+1)])

def npp_nvar(n: int):
    return n

# def gcp_data(n: int):
#     return np.array([[1.0 * (i != j) for j in range(n)] for i in range(n)])

# def gcp_nvar(n: int):
#     return n * n + n

def report(
    n: int,
    nvar: int,
    *,
    model_time: float = float('NaN'),
    compiler_time: float = float('NaN'),
    convert_time: float = float('NaN'),
    total_time: float = float('NaN'),
    sample_count: int = 1,
    warmup_count: int = 0,
    **_,
):
    print(
        f"""\
-----------------------------
Variables: {nvar} (input: {n})
Samples.............. {sample_count:7d}
Warmups.............. {warmup_count:7d}
Model................ {model_time:7.3f}
Compilation.......... {compiler_time:7.3f}
Conversion........... {convert_time:7.3f}
Total elapsed time... {total_time:7.3f}
""",
        flush=True,
    )


def tsp_info(**kwargs: dict):
    return {
        "data" : tsp_data,
        "nvar" : tsp_nvar,
        "start": 5,
        "step" : 5,
        "stop" : 100,
        **kwargs
    }


def npp_info(**kwargs: dict):
    return {
        "data" : npp_data,
        "nvar" : npp_nvar,
        "start": 5,
        "step" : 5,
        "stop" : 100,
        **kwargs
    }

# def gcp_info(**kwargs: dict):
#     return {
#         "data" : npp_data,
#         "nvar" : npp_nvar,
#         "start": 5,
#         "step" : 5,
#         "stop" : 100,
#         **kwargs
#     }

def _fieldnames(rows):
    metrics = [name for name in PHASE_COLUMNS if any(name in row for row in rows)]

    fields = ["nvar", "time"]
    fields.extend(metrics)
    fields.extend(f"time_{name}" for name in SUMMARY_STATISTICS)

    for metric in metrics:
        fields.extend(f"{metric}_{name}" for name in SUMMARY_STATISTICS)

    fields.extend(["sample_count", "warmup_count"])

    return fields


def benchmark(
    key: str,
    *,
    path: str,
    run,
    data,
    nvar,
    start: int,
    step: int,
    stop: int,
    samples: int | None = None,
    warmups: int | None = None,
    statistic: str | None = None,
):
    csv_path = Path(path).joinpath(f"results.{key}.csv")
    samples_run = sample_count() if samples is None else samples
    warmups_run = warmup_count() if warmups is None else warmups
    selected_statistic = time_statistic() if statistic is None else statistic
    rows = []

    print(f"Problem: {key}", flush=True)

    for n in range(start, stop+step, step):
        data_value = data(n)
        samples_data = collect_samples(
            run,
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

        report(n, nvar(n), **time_info)

        total_time = time_info["total_time"]
        row = {"nvar": nvar(n), **time_info}
        rows.append(row)

        if key == "npp" and total_time > 5.0:
            break
        elif key == "tsp" and total_time > 100.0:
            break

    fields = _fieldnames(rows)

    with csv_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, lineterminator="\n")
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
