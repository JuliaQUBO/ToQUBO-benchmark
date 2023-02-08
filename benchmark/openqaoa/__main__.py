import time
import numpy as np
from docplex.mp.model import Model
from openqaoa.problems.converters import FromDocplex2IsingModel
from pathlib import Path


from .. import benchmark, tsp_info, npp_info

__DIR__ = Path(__file__).parent

def tsp(n: int, D: np.ndarray, lam: float = 5.0):
    t0 = time.time()
    model = Model("tsp"+str(n))

    var_matrix = []
    for i in range(n):
        var_row = []
        for j in range(n):
            var_row += [model.binary_var("xi"+str(i)+"j"+str(j))]
        var_matrix += [var_row]

    for i in range(n):
        model.add_constraint(sum(var_matrix[i][:])==1)
    
    for j in range(n):
        model.add_constraint(sum(var_matrix[:][j])==1)

    distance = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                d = abs(i-j)
                distance += [var_matrix[k][i] * var_matrix[(k+1)%n][j]] * d
    distance = sum(distance)


    model.minimize(distance)

    # Compile Model
    t1 = time.time()

    qubo = FromDocplex2IsingModel(model)

    # Translate to QUBO
    t2 = time.time() 


    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }


def npp(n: int, s: np.ndarray, lam: float = 5.0):

    t0 = time.time()
    
    model = Model("npp"+str(n))

    x = [model.binary_var("x"+str(i)) for i in range(n)]

    H = 0
    for i in range(n):
        H += (2*x[i]-1) * s[i]
    
    H = H**2


    model.minimize(H)

    # Compile Model
    t1 = time.time()

    qubo = FromDocplex2IsingModel(model)

    # Translate to QUBO
    t2 = time.time() 


    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }


if __name__ == "__main__":
    benchmark("tsp", **tsp_info(path=__DIR__, run=tsp, start=5, step=5, stop=35))
    benchmark("npp", **npp_info(path=__DIR__, run=npp, start=20, step=20, stop=200))
