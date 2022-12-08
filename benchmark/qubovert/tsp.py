import qubovert as qv
import time
import numpy as np
import pandas as pd

def tsp(n_city):
    t0 = time.time()
    x = []

    x = [[qv.boolean_var(f"x[{i},{j}]") for j in range(n_city)] for i in range(n_city)] 

    model = 0

    # add objective function
    for i in range(n_city):
        for j in range(n_city):
            for k in range(n_city):
                d_ij = 10
                model += d_ij * x[k][i] * x[(k + 1) % n_city][j]
    
    # add constraints
    for i in range(n_city):
        model.add_constraint_lt_zero(sum(x[i]) - 1, lam=1)
        temp_sum = 0
        for j in range(n_city):
            temp_sum += x[j][i]
        model.add_constraint_lt_zero(temp_sum -1, lam=1)

    t1 = time.time()
    qubo = model.to_qubo()
    t2 = time.time()
    # print(qubo)
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