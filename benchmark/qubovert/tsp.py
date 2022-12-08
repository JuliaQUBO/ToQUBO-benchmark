import qubovert as qv
import time
import numpy as np
import pandas as pd

import time
import qubovert as qv

def tsp(n: int, lam:float = 5.0):
    t0 = time.time()
   
    # Create Model
    model = 0

    # Add variables
    x = [[qv.boolean_var(f"x[{i},{j}]") for j in range(n)] for i in range(n)]

    # Distance Matrix
    D = [[10.0 for _ in range(n)] for _ in range(n)]

    # Add objective function
    for i in range(n):
        for j in range(n):
            for k in range(n):
                model += D[i][j] * x[k][i] * x[(k + 1) % n][j]
    
    # Add constraints
    for i in range(n):
        model.add_constraint_eq_zero(sum(x[i][j] for j in range(n)) - 1, lam=lam)

    for j in range(n):
        model.add_constraint_eq_zero(sum(x[i][j] for i in range(n)) - 1, lam=lam)

    t1 = time.time()

    # Convert to QUBO
    qubo = model.to_qubo()
    
    t2 = time.time()

    return t1-t0, t2-t1

def measure(init_size, max_size, step):
    results = {"n_var":[], "time":[]}
    for n in range(init_size, max_size+step, step):
        model_time, to_qubo_time = tsp(n)
        print("Variables: ", n*n)
        print("Model: ", model_time)
        print("Convert to QUBO: ", to_qubo_time)
        print("Total elapsed time: ", model_time + to_qubo_time)
        print("----------")
        results["n_var"] += [n*n]
        results["time"] += [model_time + to_qubo_time]
    df = pd.DataFrame(results)
    df.to_csv("./benchmark/qubovert/tsp_qubovert.csv", index = False)

measure(5,100,5)