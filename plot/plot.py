import csv
import matplotlib.pyplot as plt
import scienceplots
import shutil
import numpy as np
from scipy.optimize import curve_fit
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent

BASE_PATH = ROOT_PATH.joinpath("benchmark")
DATA_PATH = ROOT_PATH.joinpath("data")

TITLE_REF = {
    "tsp": "Travelling Salesperson Problem",
    "npp": "Number Partitioning Problem",
    "gcp": "Graph Coloring Problem",
}

PSRBLUE = "#002846"
PSRGOLD = "#a49375"

COLOR_REF = {
    "toqubo"  : PSRGOLD,
    "qiskit"  : PSRBLUE,
    "openqaoa": PSRBLUE,
    "qubovert": PSRBLUE,
    "pyqubo"  : PSRBLUE,
}
LABEL_REF = {
    "toqubo"  : r"\texttt{ToQUBO.jl}",
    "qiskit"  : r"\texttt{Qiskit (docplex)}",
    "openqaoa": r"\texttt{OpenQAOA (docplex)}",
    "qubovert": r"\texttt{qubovert}",
    "pyqubo"  : r"\texttt{PyQUBO}",
}
MARKER_REF = {
    "toqubo"  : "*",
    "qiskit"  : "o",
    "openqaoa": "s",
    "qubovert": "^",
    "pyqubo"  : "d",
}

def has_latex():
    return (shutil.which("latex") is not None)

if has_latex():
    plt.rcParams.update({
        "text.usetex" : True
    })

    STYLE_FLAGS = ['science']
else:
    plt.rcParams.update({
        "text.usetex" : False
    })

    STYLE_FLAGS = ['science', 'no-latex']

def read_csv(path):
    with open(path, "r") as fp:
        reader = csv.reader(fp)
        header = list(next(reader))
        table  = {col: [] for col in header}
        for row in reader:
            for (col, val) in zip(header, row):
                if col == "nvar":
                    table[col].append(int(val))
                else:
                    table[col].append(float(val))
        return table 

def plot_benchmark(key: str):
    data = {}

    data["toqubo"]   = read_csv(BASE_PATH.joinpath("ToQUBO"  , f"results.{key}.csv"))
    data["qubovert"] = read_csv(BASE_PATH.joinpath("qubovert", f"results.{key}.csv"))
    data["pyqubo"]   = read_csv(BASE_PATH.joinpath("pyqubo"  , f"results.{key}.csv"))
    data["qiskit"]   = read_csv(BASE_PATH.joinpath("qiskit"  , f"results.{key}.csv"))
    data["openqaoa"] = read_csv(BASE_PATH.joinpath("openqaoa", f"results.{key}.csv"))

    tags = [
        "qiskit",
        "openqaoa",
        "qubovert",
        "pyqubo",
        "toqubo",
    ]

    plt.figure(figsize = (5,4))

    plt.title(TITLE_REF[key])

    plt.style.use(STYLE_FLAGS)

    if key == "tsp":
        plt.xscale('symlog')
        plt.yscale('symlog')

        # def f(n, a4, a3, a2, a1, a0):
        #     return a4 * n ** 4 + a3 * n ** 3 + a2 * n ** 2 + a1 * n + a0

        def f(n, a4, a3, a2, a1, a0):
            return a4 * n ** 4 + a3 * n ** 3 + a2 * n ** 2 + a1 * n + a0

    elif key == "npp":
        def f(n, a2, a1, a0):
            return a2 * n ** 2 + a1 * n + a0
    else:
        pass

    xl = yl = +float("inf")
    xu = yu = -float("inf")

    for tag in tags:
        color  = COLOR_REF.get(tag, "#002846") # PSRBLUE
        marker = MARKER_REF.get(tag)
        label  = LABEL_REF.get(tag)
        line   = "--"

        n = np.array(data[tag]["nvar"], dtype=int)
        t = np.array(data[tag]["time"], dtype=float)

        xl = min(xl, np.min(n))
        yl = min(yl, np.min(t))
        xu = max(xu, np.max(n))
        yu = max(yu, np.max(t))

        p, _ = curve_fit(f, n, t)

        x = np.array(data["toqubo"]["nvar"], dtype=int)
        y = f(x, *p)

        plt.plot(x, y,    color = color, linestyle = line)
        plt.scatter(n, t, color = color, marker = marker)
        plt.plot([], [],  color = color, marker = marker, linestyle = line, label = label)

    plt.ylim(yl, yu)
    plt.xlim(xl, xu)

    plt.xlabel(r"\texttt{\#variables}")
    plt.ylabel("Building Time (sec)")
    plt.grid(True)

    legend = plt.legend(loc = "best")
    frame = legend.get_frame()
    frame.set_facecolor("white")

    DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(str(DATA_PATH.joinpath(f"results.{key}.pdf")))
    plt.savefig(str(DATA_PATH.joinpath(f"results.{key}.png")), dpi=300)

    return None

def plot_toqubo(key: str):
    toqubo_data = read_csv(BASE_PATH.joinpath("ToQUBO", f"results.{key}.csv"))

    plt.figure(figsize = (5,4))

    plt.style.use(STYLE_FLAGS)

    plt.plot(toqubo_data["nvar"], toqubo_data["toqubo_time"], label = "ToQUBO", marker='D')
    plt.plot(toqubo_data["nvar"], toqubo_data["jump_time"]  , label = "JuMP"  , marker='D')
    
    if key == "tsp":
        plt.xscale('symlog')
        plt.yscale('symlog')

    plt.xlabel(r"\#variables")
    plt.ylabel("Running Time (sec)")
    plt.grid(True)
    
    legend = plt.legend()
    frame = legend.get_frame()
    frame.set_facecolor("white")

    DATA_PATH.mkdir(parents=True, exist_ok=True)

    plt.savefig(str(DATA_PATH.joinpath(f"toqubo.{key}.pdf")))
    plt.savefig(str(DATA_PATH.joinpath(f"toqubo.{key}.png")), dpi=300)

    return None

if __name__ == "__main__":
    for key in ["tsp", "npp"]:
        plot_benchmark(key)
        plot_toqubo(key)
