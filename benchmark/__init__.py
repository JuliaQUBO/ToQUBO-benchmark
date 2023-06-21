# Standard Library
import gc
from pathlib import Path

# Third-party
import numpy as np

def tsp_data(n: int):
    return np.array([[abs(i - j) for j in range(n)] for i in range(n)])

def tsp_nvar(n: int):
    return n * n

def npp_data(n: int):
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
):
    print(
        f"""\
-----------------------------
Variables: {nvar} (input: {n})
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

def benchmark(key: str, *, path: str, run, data, nvar, start: int, step: int, stop: int):
    csv_path = Path(path).joinpath(f"results.{key}.csv")

    print(f"Problem: {key}", flush=True)

    with csv_path.open("w") as fp:
        print("nvar,time", file=fp)

        for n in range(start, stop+step, step):
            gc.collect()
            gc.disable()
            
            time_info = run(n, data(n))

            gc.enable()

            report(n, nvar(n), **time_info)

            total_time = time_info["total_time"]

            print(f"{nvar(n)},{total_time}", file=fp)

            if key == "npp" and total_time > 5.0:
                break
            elif key == "tsp" and total_time > 100.0:
                break