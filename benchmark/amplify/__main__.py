import time
import numpy as np
from pathlib import Path
from amplify import BinaryPoly, BinaryQuadraticModel, gen_symbols, sum_poly
from amplify.constraint import equal_to

from .. import benchmark, tsp_info, npp_info

__DIR__ = Path(__file__).parent

def tsp(n: int, D: np.ndarray, lam: float = 5.0):
    # Create Model
    t0 = time.time()
    x  = gen_symbols(BinaryPoly, n, n)

    # Constraints on rows
    row_constraints = [
        equal_to(sum_poly([x[k][i] for i in range(n)]), 1) for k in range(n)
    ]

    # Constraints on columns
    col_constraints = [
        equal_to(sum_poly([x[k][i] for k in range(n)]), 1) for i in range(n)
    ]

    constraints = sum(row_constraints) + sum(col_constraints)

    # Objective Value
    cost = sum_poly(
        n,
        lambda k: sum_poly(
            n,
            lambda i: sum_poly(
                n, lambda j: D[i][j] * x[k][i] * x[(k + 1) % n][j]
            ),
        ),
    )

    # Construct hamiltonian
    f = cost + lam * constraints

    # Compile Model
    t1 = time.time()

    model = BinaryQuadraticModel(f)

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
    x  = gen_symbols(BinaryPoly, n)

    # Objective Value / Construct hamiltonian
    f = (sum((2 * x[i] - 1) * s[i] for i in range(n))) ** 2

    # Compile Model
    t1 = time.time()

    model = BinaryQuadraticModel(f)

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
