import time
import numpy as np
from pathlib import Path
from amplify import Model, VariableGenerator, equal_to
from amplify import sum as amplify_sum

from .. import benchmark, tsp_info, npp_info

__DIR__ = Path(__file__).parent

def tsp(n: int, D: np.ndarray, lam: float = 5.0):
    # Create Model
    t0 = time.time()
    gen = VariableGenerator()
    x = gen.array("Binary", n, n)

    # Constraints on rows
    row_constraints = equal_to(x, 1, axis=1)

    # Constraints on columns
    col_constraints = equal_to(x, 1, axis=0)

    constraints = row_constraints + col_constraints

    # Objective Value
    cost = amplify_sum(
        D[i][j] * x[k, i] * x[(k + 1) % n, j]
        for k in range(n)
        for i in range(n)
        for j in range(n)
    )

    # Construct model
    f = Model(cost, lam * constraints)

    # Compile Model
    t1 = time.time()

    model = f.to_unconstrained_poly()

    # Stop the count!
    t2 = time.time()

    return {
        "model_time"   : t1 - t0,
        "convert_time" : t2 - t1,
        "total_time"   : t2 - t0,
    }

def npp(n: int, s: np.ndarray, lam: float = 5.0):
    # Create Model
    t0 = time.time()
    gen = VariableGenerator()
    x = gen.array("Binary", n)

    # Objective Value / Construct hamiltonian
    f = amplify_sum((2 * x[i] - 1) * s[i] for i in range(n)) ** 2

    # Compile Model
    t1 = time.time()

    model = Model(f).to_unconstrained_poly()

    # Stop the count!
    t2 = time.time()

    return {
        "model_time"   : t1 - t0,
        "convert_time" : t2 - t1,
        "total_time"   : t2 - t0,
    }

if __name__ == "__main__":
    benchmark("tsp", **tsp_info(path=__DIR__, run=tsp, start=5, step=5, stop=100))
    benchmark("npp", **npp_info(path=__DIR__, run=npp, start=20, step=20, stop=1_000))
