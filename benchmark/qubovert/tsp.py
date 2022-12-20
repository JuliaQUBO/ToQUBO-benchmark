import time
import pandas   as pd
import numpy    as np
import qubovert as qv
from pathlib import Path

__DIR__ = Path(__file__).parent

def tsp(n: int, lam:float = 5.0):
    # Problem Data
    D = 10.0 * np.ones((n, n), dtype=float)

    # Create Model
    t0 = time.time()
    
    model = 0.0

    # Add variables
    x = [[qv.boolean_var(f"x[{i},{j}]") for j in range(n)] for i in range(n)]

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

    # Convert to QUBO
    t1 = time.time()
    
    qubo = model.to_qubo()
    
    # Stop the count!
    t2 = time.time()

    return t1-t0, t2-t1

def main(init_size, max_size, step):
    results = {"nvar":[], "time":[]}

    for n in range(init_size, max_size+step, step):
        model_time, compiler_time, convert_time = tsp(n)
        total_time = model_time + compiler_time + convert_time

        print(
f"""\
-----------------------------
Variables: {n * n} ({n} sites)
Model................ {model_time:7.3f}
Compilation.......... {compiler_time:7.3f}
Conversion........... {convert_time:7.3f}
Total elapsed time... {total_time:7.3f}
""",
flush = True
        )

        results["nvar"].append(n * n)
        results["time"].append(total_time)

    df = pd.DataFrame(results)
    df.to_csv(__DIR__.joinpath("results.csv"), index = False)

if __name__ == '__main__':
    main(5, 100, 5)
