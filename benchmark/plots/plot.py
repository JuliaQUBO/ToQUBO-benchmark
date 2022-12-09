import matplotlib.pyplot as plt
import scienceplots
from pandas import read_csv
from pathlib import Path

BASE_PATH = Path.cwd().joinpath("benchmark")

def plot_benchmark():
    toqubo_data         = read_csv(BASE_PATH.joinpath("ToQUBO"    , "tsp_ToQUBO.csv"))
    pyqubo_current_data = read_csv(BASE_PATH.joinpath("pyqubo"    , "tsp_pyqubo.csv"))
    pyqubo_040_data     = read_csv(BASE_PATH.joinpath("pyqubo_040", "tsp_pyqubo_040.csv"))
    qubovert_data       = read_csv(BASE_PATH.joinpath("qubovert"  , "tsp_qubovert.csv"))

    plt.figure(figsize = (5,4))

    plt.style.use(['science','no-latex'])

    plt.plot(
        toqubo_data["n_var"],
        toqubo_data["time"],
        label = "ToQUBO 0.1.3",
        marker='o'
    )
    plt.plot(
        toqubo_data["n_var"],
        toqubo_data["toqubo_time"],
        label = "ToQUBO* 0.1.3",
        marker='o'
    )
    plt.plot(
        pyqubo_040_data["n_var"],
        pyqubo_040_data["time"],
        label = "PyQUBO 0.4.0",
        marker='o'
    )
    plt.plot(
        pyqubo_current_data["n_var"],
        pyqubo_current_data["time"],
        label = "PyQUBO 1.3.1",
        marker='o'
    )
    plt.plot(
        qubovert_data["n_var"],
        qubovert_data["time"],
        label = "qubovert 1.2.5",
        marker='o'
    )

    plt.xscale('symlog')
    plt.yscale('symlog')
    plt.xlabel("#variables")
    plt.ylabel("Execution Time (sec)")
    plt.grid(True)
    plt.legend()
    plt.savefig(BASE_PATH.joinpath('benchmark.png'))

    return None

def plot_toqubo():
    toqubo_data = read_csv(BASE_PATH.joinpath("ToQUBO", "tsp_ToQUBO.csv"))

    plt.figure(figsize = (5,4))

    plt.style.use(['science','no-latex'])

    plt.plot(toqubo_data["n_var"], toqubo_data["toqubo_time"], label = "ToQUBO", marker='D')
    plt.plot(toqubo_data["n_var"], toqubo_data["jump_time"]  , label = "JuMP"  , marker='D')
    plt.xscale('symlog')
    plt.yscale('symlog')
    plt.xlabel("#variables")
    plt.ylabel("Execution Time (sec)")
    plt.grid(True)
    plt.legend()
    plt.savefig(BASE_PATH.joinpath('toqubo.png'))

    return None

if __name__ == "__main__":
    plot_benchmark()
    plot_toqubo()