import time
import pandas as pd
from pyqubo  import Array, Constraint, Placeholder
from pathlib import Path

__DIR__ = Path(__file__).parent

def tsp(n):
    # Problem Data
    D  = [[10.0 for j in range(n)] for i in range(n)]

    # Create Model
    t0 = time.time()
    x  = Array.create('c', (n, n), 'BINARY')

    # Constraint not to visit more than two cities at the same time.
    time_const = 0.0
    for i in range(n):
        # If you wrap the hamiltonian by Const(...), this part is recognized as constraint
        time_const += Constraint((sum(x[i,j] for j in range(n)) - 1)**2, label="time{}".format(i))

    # Constraint not to visit the same city more than twice.
    city_const = 0.0
    for j in range(n):
        city_const += Constraint((sum(x[i,j] for i in range(n)) - 1)**2, label="city{}".format(j))

    # Objective Value
    distance = sum(
        D[i][j] * x[k, i] * x[(k+1)%n,j]
        for i in range(n)
        for j in range(n)
        for k in range(n)
    )
    
    # Construct hamiltonian
    # A = Placeholder("A") 
    # NOTE: Using a placeholder is not working on Linux!
    A = 2.0 
    H = distance + A * (time_const + city_const)

    # Also, no need for passing a value for "A" as in
    # feed_dict = {"A":  2.0}
    feed_dict = {}

    # Compile Model
    t1 = time.time()

    model = H.compile()

    # Translate to QUBO
    t2 = time.time()

    qubo, offset = model.to_qubo(feed_dict=feed_dict)

    # Stop the count!
    t3 = time.time()

    return t1-t0, t2-t1, t3-t2

def main(init_size, max_size, step):
    results = {"n_var":[], "time":[]}

    for n in range(init_size, max_size+step, step):
        model_time, compiler_time, to_qubo_time = tsp(n)
        total_time = model_time + compiler_time + to_qubo_time

        print(
            f"""
            -------------------------------------
            Variables: {n * n}
            Model................ {model_time}
            Compilation.......... {compiler_time}
            Conversion........... {to_qubo_time}
            Total elapsed time... {total_time}
            """,
            flush = True
        )

        results["n_var"].append(n * n)
        results["time"].append(total_time)

    df = pd.DataFrame(results)
    df.to_csv(__DIR__.joinpath("results.csv"), index = False)

if __name__ == '__main__':
    main(5, 100, 5)
