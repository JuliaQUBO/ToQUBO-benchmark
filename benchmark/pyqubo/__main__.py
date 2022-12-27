import time
import numpy as np
from pyqubo  import Array, Constraint
from pathlib import Path

from .. import benchmark, tsp_info, npp_info

__DIR__ = Path(__file__).parent

def tsp(n: int, D: np.ndarray, lam: float = 5.0):
    # Create Model
    t0 = time.time()
    x  = Array.create("c", (n, n), "BINARY")

    # Constraint not to visit more than two cities at the same time.
    time_const = 0.0
    for i in range(n):
        # If you wrap the hamiltonian by Const(...), this part is recognized as constraint
        time_const += Constraint((sum(x[i, :]) - 1) ** 2, label="time{}".format(i))

    # Constraint not to visit the same city more than twice.
    city_const = 0.0
    for k in range(n):
        city_const += Constraint((sum(x[:, k]) - 1) ** 2, label="city{}".format(k))

    # Objective Value
    distance = sum(x[:, k].T @ D @ x[:, (k + 1) % n] for k in range(n))

    # Construct hamiltonian
    # A = Placeholder("A")
    # NOTE: Using a placeholder is not working on Linux!
    A = 2.0
    H = distance + A * (time_const + city_const)

    # Compile Model
    t1 = time.time()

    model = H.compile()

    # Translate to QUBO
    t2 = time.time()

    qubo, offset = model.to_qubo()

    # Stop the count!
    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }

def npp(n: int, s: np.ndarray, lam: float = 5.0):
    # Create Model
    t0 = time.time()
    x  = Array.create("c", n, "BINARY")

    # Objective Value / Construct hamiltonian
    H = ((2 * x - 1) @ s) ** 2

    # Compile Model
    t1 = time.time()

    model = H.compile()

    # Translate to QUBO
    t2 = time.time()

    qubo, offset = model.to_qubo()

    # Stop the count!
    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }

if __name__ == "__main__":
    benchmark("tsp", **tsp_info(path=__DIR__, run=tsp, start=5, step=5, stop=100))
    benchmark("npp", **npp_info(path=__DIR__, run=npp, start=10, step=10, stop=1_000))
