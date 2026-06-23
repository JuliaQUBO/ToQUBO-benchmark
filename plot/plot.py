import csv
import sys
import subprocess
import matplotlib.pyplot as plt
import scienceplots
import shutil
import numpy as np
from scipy.optimize import curve_fit
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent

def get_path_arg(flag, default):
    if flag not in sys.argv:
        return default

    index = sys.argv.index(flag)

    try:
        value = sys.argv[index + 1]
    except IndexError as exc:
        raise SystemExit(f"{flag} requires a path") from exc

    path = Path(value)

    if not path.is_absolute():
        path = ROOT_PATH.joinpath(path)

    return path

BASE_PATH = get_path_arg("--results-dir", ROOT_PATH.joinpath("benchmark"))
DATA_PATH = get_path_arg("--output-dir", ROOT_PATH.joinpath("data"))

TITLE_REF = {
        "tsp": {"en": "Travelling Salesperson Problem", "pt": "Problema do Caixeiro-viajante"},
        "npp": {"en": "Number Partitioning Problem", "pt": "Problema da Partição de Números"}
}

GREEN = "#169E4D"
RED = "#BE1D2C"
PURPLE = "#642F8F"
BROWN = "#AE6F2B"
PINK = "#901F63"
BLUE = "#1897D4"
ORANGE = "#FBB03F"

COLOR_REF = {
    "qiskit"  : GREEN,
    "openqaoa": RED,
    "qubovert": PURPLE,
    "pyqubo"  : BROWN,
    "amplify" : PINK,
    "dwave"   : ORANGE,
    "toqubo"  : BLUE,
}
LABEL_REF = {
    "qiskit"  : "Qiskit (docplex)",
    "openqaoa": "OpenQAOA (docplex)",
    "qubovert": "qubovert",
    "pyqubo"  : "PyQUBO",
    "amplify" : "amplify",
    "dwave"   : "dimod",
    "toqubo"  : "ToQUBO.jl",
}
MARKER_REF = {
    "qiskit"  : "X",
    "openqaoa": "^",
    "qubovert": "s",
    "pyqubo"  : "d",
    "amplify" : "h",
    "dwave"   : "P",
    "toqubo"  : "*",
}

def has_latex():
    if shutil.which("latex") is None or shutil.which("kpsewhich") is None:
        return False

    for package in ("type1cm.sty", "type1ec.sty"):
        result = subprocess.run(
            ["kpsewhich", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        if result.returncode != 0:
            return False

    return True

def get_lang():
    if "pt" in sys.argv:
        return "pt"
    else:
        return "en"

def is_simple():
    return "simple" in sys.argv

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

def maybe_read_csv(package, key):
    path = BASE_PATH.joinpath(package, f"results.{key}.csv")

    if path.exists():
        return read_csv(path)
    else:
        return None

def plot_benchmark(key: str, ax):
    data = {
        "qiskit"  : maybe_read_csv("qiskit", key),
        "openqaoa": maybe_read_csv("openqaoa", key),
        "qubovert": maybe_read_csv("qubovert", key),
        "pyqubo"  : maybe_read_csv("pyqubo", key),
        "amplify" : maybe_read_csv("amplify", key),
        "dwave"   : maybe_read_csv("dwave", key),
        "toqubo"  : maybe_read_csv("ToQUBO", key),
    }

    data = {tag: table for tag, table in data.items() if table is not None}

    if is_simple():
        tags = ["qubovert", "pyqubo", "amplify", "toqubo"]
        LABEL_REF["toqubo"] = "QUBO.jl"
    else:
        tags = list(data.keys())
    lang = get_lang()

    ax.set_title(TITLE_REF[key][lang])

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
        line   = ":"

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

    if lang == "en":
        ax.set_xlabel("#variables")
        ax.set_ylabel("Building Time (sec)")
    elif lang == "pt":
        ax.set_xlabel("#variaveis")
        ax.set_ylabel("Tempo de Montagem (seg)")
    ax.grid(True)

    return handles

def plot_toqubo(key: str, ax):
    toqubo_data = maybe_read_csv("ToQUBO", key)
    amplify_data = maybe_read_csv("amplify", key)

    if toqubo_data is not None:
        has_phase_split = "compiler_time" in toqubo_data and "convert_time" in toqubo_data

        ax.plot(toqubo_data["nvar"], toqubo_data["time"], label="JuMP + ToQUBO", marker='*')
        ax.plot(toqubo_data["nvar"], toqubo_data["jump_time"], label="JuMP", marker='D')

        if has_phase_split:
            ax.plot(toqubo_data["nvar"], toqubo_data["compiler_time"], label="ToQUBO optimize!", marker='o')
            ax.plot(toqubo_data["nvar"], toqubo_data["convert_time"], label="Backend extraction", marker='s')
        else:
            ax.plot(toqubo_data["nvar"], toqubo_data["toqubo_time"], label="ToQUBO", marker='D')

    if amplify_data is not None:
        ax.plot(amplify_data["nvar"], amplify_data["time"], label="Amplify", marker='X')

    if key == "tsp":
        ax.set_xscale('symlog')
        ax.set_yscale('symlog')

    ax.set_xlabel("#variables")
    ax.set_ylabel("Running Time (sec)")
    ax.grid(True)

    handles, _ = ax.get_legend_handles_labels()

    if handles:
        legend = ax.legend(loc="best")
        frame = legend.get_frame()
        frame.set_facecolor("white")

    return None

if __name__ == "__main__":
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    if is_simple():
        fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    else:
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    handles = []

    for i, key in enumerate(["tsp", "npp"]):
        h = plot_benchmark(key, axs[i])

        handles.append(h)

    if is_simple():
        fig.subplots_adjust(bottom=0.25, wspace=0.2, left=0.05, right=0.95)
    else:
        fig.subplots_adjust(bottom=0.2, wspace=0.2, left=0.05, right=0.95)
    
    fig.legend(
        handles = handles[0],
        loc='center',
        bbox_to_anchor=(0.5, 0.075),
        bbox_transform=fig.transFigure,
        ncol=7,
        shadow=True,
    )

    # plt.tight_layout()
    plt.savefig(str(DATA_PATH.joinpath("results.pdf")))
    plt.savefig(str(DATA_PATH.joinpath("results.png")), dpi=300)
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    for i, key in enumerate(["tsp", "npp"]):
        plot_toqubo(key, axs[i])

    plt.tight_layout()
    plt.savefig(str(DATA_PATH.joinpath("results.toqubo.pdf")))
    plt.savefig(str(DATA_PATH.joinpath("results.toqubo.png")), dpi=300)
    plt.close(fig)

    for key in ["tsp", "npp"]:
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        handles = plot_benchmark(key, ax)

        if handles:
            legend = ax.legend(handles=handles, loc="best")
            frame = legend.get_frame()
            frame.set_facecolor("white")

        plt.tight_layout()
        plt.savefig(str(DATA_PATH.joinpath(f"results.{key}.pdf")))
        plt.savefig(str(DATA_PATH.joinpath(f"results.{key}.png")), dpi=300)
        plt.close(fig)

        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        plot_toqubo(key, ax)
        plt.tight_layout()
        plt.savefig(str(DATA_PATH.joinpath(f"toqubo.{key}.pdf")))
        plt.savefig(str(DATA_PATH.joinpath(f"toqubo.{key}.png")), dpi=300)
        plt.close(fig)
