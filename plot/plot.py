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
}

PSRBLUE = "#002846"
PSRGOLD = "#a49375"

COLOR_REF = {
    "toqubo"  : PSRGOLD,
    "qiskit"  : PSRBLUE,
    "openqaoa": PSRBLUE,
    "qubovert": PSRBLUE,
    "pyqubo"  : PSRBLUE,
    "amplify" : PSRBLUE,
}
LABEL_REF = {
    "toqubo"  : r"\texttt{ToQUBO.jl}",
    "qiskit"  : r"\texttt{Qiskit (docplex)}",
    "openqaoa": r"\texttt{OpenQAOA (docplex)}",
    "qubovert": r"\texttt{qubovert}",
    "pyqubo"  : r"\texttt{PyQUBO}",
    "amplify": r"\texttt{amplify}",
}
MARKER_REF = {
    "toqubo"  : "*",
    "qiskit"  : "o",
    "openqaoa": "s",
    "qubovert": "^",
    "pyqubo"  : "d",
    "amplify" : "h",
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

def plot_benchmark(key: str, ax):
    data = {}

    data["toqubo"]   = read_csv(BASE_PATH.joinpath("ToQUBO"  , f"results.{key}.csv"))
    data["qubovert"] = read_csv(BASE_PATH.joinpath("qubovert", f"results.{key}.csv"))
    data["pyqubo"]   = read_csv(BASE_PATH.joinpath("pyqubo"  , f"results.{key}.csv"))
    data["qiskit"]   = read_csv(BASE_PATH.joinpath("qiskit"  , f"results.{key}.csv"))
    data["openqaoa"] = read_csv(BASE_PATH.joinpath("openqaoa", f"results.{key}.csv"))
    data["amplify"]  = read_csv(BASE_PATH.joinpath("amplify" , f"results.{key}.csv"))

    tags = list(data.keys())

    ax.set_title(TITLE_REF[key])

    if key == "tsp":
        ax.set_xscale('symlog')
        ax.set_yscale('symlog')

    xl = yl = +float("inf")
    xu = yu = -float("inf")

    handles = []

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

        ax.plot(n, t, color=color, linestyle=line)
        ax.scatter(n, t, color=color, marker=marker)

        h, = ax.plot([], [], color=color, marker=marker, linestyle=line, label=label)

        handles.append(h)

    ax.set_ylim(yl, yu)
    ax.set_xlim(xl, xu)

    ax.set_xlabel(r"\texttt{\#variables}")
    ax.set_ylabel("Building Time (sec)")
    ax.grid(True)

    return handles

def plot_toqubo(key: str, ax):
    toqubo_data = read_csv(BASE_PATH.joinpath("ToQUBO", f"results.{key}.csv"))

    ax.plot(toqubo_data["nvar"], toqubo_data["toqubo_time"], label="ToQUBO", marker='D')
    ax.plot(toqubo_data["nvar"], toqubo_data["jump_time"], label="JuMP", marker='D')

    ax.set_xscale('symlog')
    ax.set_yscale('symlog')

    ax.set_xlabel(r"\#variables")
    ax.set_ylabel("Running Time (sec)")
    ax.grid(True)

    legend = ax.legend(loc="best")
    frame = legend.get_frame()
    frame.set_facecolor("white")

    return None

if __name__ == "__main__":
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    handles = []

    for i, key in enumerate(["tsp", "npp"]):
        h = plot_benchmark(key, axs[i])

        handles.append(h)

    fig.subplots_adjust(bottom=0.2, wspace=0.2, left=0.05, right=0.95)
    fig.legend(
        handles = handles[0],
        loc='center',
        bbox_to_anchor=(0.5, 0.075),
        bbox_transform=fig.transFigure,
        ncol=5,
        shadow=True,
    )

    # plt.tight_layout()
    plt.savefig(str(DATA_PATH.joinpath("results.pdf")))
    plt.savefig(str(DATA_PATH.joinpath("results.png")), dpi=300)

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    for i, key in enumerate(["tsp", "npp"]):
        plot_toqubo(key, axs[i])

    plt.tight_layout()
    plt.savefig(str(DATA_PATH.joinpath("results.toqubo.pdf")))
    plt.savefig(str(DATA_PATH.joinpath("results.toqubo.png")), dpi=300)
