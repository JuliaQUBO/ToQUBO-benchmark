import matplotlib.pyplot as plt
import scienceplots
import shutil
from pandas import read_csv
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent

BASE_PATH = ROOT_PATH.joinpath("benchmark")
DATA_PATH = ROOT_PATH.joinpath("data")

TITLE_REF = {
    "tsp": "Travelling Salesperson Problem",
    "npp": "Number Partitioning Problem",
    "gcp": "Graph Coloring Problem",
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

def plot_benchmark(key: str):
    toqubo_data         = read_csv(BASE_PATH.joinpath("ToQUBO"  , f"results.{key}.csv"))
    qubovert_data       = read_csv(BASE_PATH.joinpath("qubovert", f"results.{key}.csv"))
    pyqubo_current_data = read_csv(BASE_PATH.joinpath("pyqubo"  , f"results.{key}.csv"))

    plt.figure(figsize = (5,4))

    plt.title(TITLE_REF[key])

    plt.style.use(STYLE_FLAGS)

    plt.plot(
        qubovert_data["nvar"],
        qubovert_data["time"],
        label  = r"\texttt{qubovert}",
        color  = "#546670", # PSRGRAY
        marker ='o',
    )
    plt.plot(
        pyqubo_current_data["nvar"],
        pyqubo_current_data["time"],
        label  = r"\texttt{PyQUBO}",
        color  = "#002846", # PSRBLUE
        marker ='o',
    )
    plt.plot(
        toqubo_data["nvar"],
        toqubo_data["time"],
        label  = r"\texttt{ToQUBO.jl}",
        color  ="#a49375", # PSRGOLD
        marker ='o',
    )

    if key == "tsp":
        plt.xscale('symlog')
        plt.yscale('symlog')

    plt.xlabel(r"\texttt{\#variables}")
    plt.ylabel("Building Time (sec)")
    plt.grid(True)

    legend = plt.legend()
    frame = legend.get_frame()
    frame.set_facecolor("white")
    
    plt.savefig(str(DATA_PATH.joinpath(f"results.{key}.pdf")))
    plt.savefig(str(DATA_PATH.joinpath(f"results.{key}.png")))

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

    plt.savefig(str(DATA_PATH.joinpath(f"toqubo.{key}.pdf")))
    plt.savefig(str(DATA_PATH.joinpath(f"toqubo.{key}.png")))

    return None

if __name__ == "__main__":
    for key in ["tsp", "npp"]:
        plot_benchmark(key)
        plot_toqubo(key)