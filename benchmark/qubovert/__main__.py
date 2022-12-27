import sys
import time
import numpy as np
import qubovert as qv
from pathlib import Path

__DIR__ = Path(__file__).parent

from .. import benchmark, tsp_info, npp_info

def tsp(n: int, D: np.ndarray, lam: float = 5.0):
    # Create Model
    t0 = time.time()

    # Add variables
    x = np.array([[qv.boolean_var(f"x[{i},{k}]") for k in range(n)] for i in range(n)])

    # Add objective function
    model = sum(x[:,k] @ D @ x[:,(k + 1) % n] for k in range(n))

    # Add constraints
    for i in range(n):
        model.add_constraint_eq_zero(sum(x[i,:]) - 1, lam=lam)

    for k in range(n):
        model.add_constraint_eq_zero(sum(x[:,k]) - 1, lam=lam)

    # Convert to QUBO
    t1 = time.time()

    qubo = model.to_qubo()

    # Stop the count!
    t2 = time.time()

    return {
        "model_time": t1 - t0,
        "convert_time": t2 - t1,
        "total_time": t2 - t0,
    }

def npp(n: int, s: np.ndarray):
    # Create Model
    t0 = time.time()

    # Add variables
    x = np.array([qv.boolean_var(f"x[{i}]") for i in range(n)])

    # Add objective function
    model = ((2 * x - 1) @ s) ** 2

    # Convert to QUBO
    t1 = time.time()

    qubo = model.to_qubo()

    # Stop the count!
    t2 = time.time()

    return {
        "model_time": t1 - t0,
        "convert_time": t2 - t1,
        "total_time": t2 - t0,
    }

if __name__ == "__main__":
    benchmark("tsp", **tsp_info(path=__DIR__, run=tsp, start=5, step=5, stop=50))
    benchmark("npp", **npp_info(path=__DIR__, run=npp, start=20, step=20, stop=500))
