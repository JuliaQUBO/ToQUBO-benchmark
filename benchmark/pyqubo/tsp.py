import time
import pandas as pd
import numpy  as np
from pyqubo  import Array, Constraint, Placeholder
from pathlib import Path

__DIR__ = Path(__file__).parent

def tsp(n_city):
    t0 = time.time()
    x = Array.create('c', (n_city, n_city), 'BINARY')
    use_for_loop=False

    # Constraint not to visit more than two cities at the same time.
    time_const = 0.0
    for i in range(n_city):
        # If you wrap the hamiltonian by Const(...), this part is recognized as constraint
        time_const += Constraint((sum(x[i, j] for j in range(n_city)) - 1)**2, label="time{}".format(i))

    # Constraint not to visit the same city more than twice.
    city_const = 0.0
    for j in range(n_city):
        city_const += Constraint((sum(x[i, j] for i in range(n_city)) - 1)**2, label="city{}".format(j))

    # distance of route
    feed_dict = {}
    
    if use_for_loop:
        distance = 0.0
        for i in range(n_city):
            for j in range(n_city):
                for k in range(n_city):
                    # we set the constant distance
                    d_ij = 10
                    distance += d_ij * x[k, i] * x[(k + 1) % n_city, j]
                
    else:
        distance = []
        for i in range(n_city):
            for j in range(n_city):
                for k in range(n_city):
                    # we set the constant distance
                    d_ij = 10
                    distance.append(d_ij * x[k, i] * x[(k + 1) % n_city, j])
        distance = sum(distance)

    print("express done")
    
    # Construct hamiltonian
    A = Placeholder("A")
    H = distance

    feed_dict["A"] = 1.0

    # Compile model
    t1 = time.time()
    model = H.compile()
    t2 = time.time()
    qubo, offset = model.to_qubo(index_label=False, feed_dict=feed_dict)
    t3 = time.time()

    print("len(qubo)", len(qubo))

    return t1-t0, t2-t1, t3-t2

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
