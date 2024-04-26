import time
import numpy as np
import dimod
from pathlib import Path


from .. import benchmark, tsp_info, npp_info

# Reference:
# https://docs.ocean.dwavesys.com/en/stable/docs_binarycsp/intro.html

__DIR__ = Path(__file__).parent

def tsp(n: int, D: np.ndarray, lam: float = 5.0):
    t0 = time.time()
    
    model = dimod.ConstrainedQuadraticModel()

    var_matrix = [[dimod.Binary(f"x({i},{j})") for j in range(n)] for i in range(n)]

    for i in range(n):
        model.add_constraint(sum(var_matrix[i][:]) == 1)
    
    for j in range(n):
        model.add_constraint(sum(var_matrix[:][j]) == 1)

    distance = []

    for i in range(n):
        for j in range(n):
            for k in range(n):
                distance.append(var_matrix[k][i] * var_matrix[(k+1)%n][j] * D[i, j])

    distance = sum(distance)

    # This is already following the minimization sense
    model.set_objective(distance)

    # Compile Model
    t1 = time.time()

    bqm = dimod.cqm_to_bqm(model, lam)

    # Translate to QUBO
    t2 = time.time() 

    qubo = bqm.to_qubo()

    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }


def npp(n: int, s: np.ndarray, lam: float = 5.0):

    t0 = time.time()
    
    model = dimod.BinaryQuadraticModel()

    x = [dimod.Binary(f"x({i})") for i in range(n)]    
    H = sum((2*x[i]-1) * s[i] for i in range(n))**2

    model.set_objective(H)

    # Compile Model
    t1 = time.time()

    # Translate to QUBO
    t2 = time.time() 

    qubo = model.to_qubo()

    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }


if __name__ == "__main__":
    benchmark("tsp", **tsp_info(path=__DIR__, run=tsp, start=5, step=5, stop=100))
    benchmark("npp", **npp_info(path=__DIR__, run=npp, start=20, step=20, stop=1000))
