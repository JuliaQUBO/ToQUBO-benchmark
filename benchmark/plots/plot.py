import matplotlib.pyplot as plt
import scienceplots
from pandas import read_csv
from pathlib import Path

BASE_PATH = Path.cwd().joinpath("benchmark")

TITLE_REF = {
    "tsp": "Travelling Salesperson Problem",
    "npp": "Number Partitioning Problem",
}

plt.rcParams.update({
    "text.usetex" : True
})

def plot_benchmark(key: str):
    toqubo_data         = read_csv(BASE_PATH.joinpath("ToQUBO"    , f"results.{key}.csv"))
    pyqubo_current_data = read_csv(BASE_PATH.joinpath("pyqubo"    , f"results.{key}.csv"))
    # pyqubo_040_data     = read_csv(BASE_PATH.joinpath("pyqubo_040", f"results.{key}.csv"))
    qubovert_data       = read_csv(BASE_PATH.joinpath("qubovert"  , f"results.{key}.csv"))

    plt.figure(figsize = (5,4))

    plt.title(TITLE_REF[key])

    plt.style.use(['science'])

    # plt.plot(
    #     toqubo_data["nvar"],
    #     toqubo_data["toqubo_time"],
    #     label = r"ToQUBO",
    #     marker='o'
    # )
    # plt.plot(
    #     pyqubo_040_data["nvar"],
    #     pyqubo_040_data["time"],
    #     label  = r"\texttt{PyQUBO 0.4.0}",
    #     color  = "#2a838a", # PSRLIGHTGREEN
    #     marker = 'o',
    # )
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

    plt.show()

    # Reorder Legend
    # handles, labels = plt.gca().get_legend_handles_labels()
    # legend_order    = [3,2,0,1]

    # plt.legend(
    #     [handles[i] for i in legend_order],
    #     [labels[i]  for i in legend_order],
    # )
    # plt.savefig(str(BASE_PATH.joinpath(f"results.{key}.pdf")))
    # plt.savefig(str(BASE_PATH.joinpath(f"results.{key}.png")))

    return None

def plot_toqubo(key: str):
    toqubo_data = read_csv(BASE_PATH.joinpath("ToQUBO", f"results.{key}.csv"))

    plt.figure(figsize = (5,4))

    plt.style.use(['science'])

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

    plt.savefig(str(BASE_PATH.joinpath(f"toqubo.{key}.pdf")))
    plt.savefig(str(BASE_PATH.joinpath(f"toqubo.{key}.png")))

    return None

if __name__ == "__main__":
    plot_benchmark("tsp")
    plot_benchmark("npp")
    plot_toqubo("tsp")
    plot_toqubo("npp")
