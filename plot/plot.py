import csv
import math
import sys
import subprocess
import matplotlib.pyplot as plt
import scienceplots
import shutil
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

def variable_count_label(lang):
    label = "#variables" if lang == "en" else "#variaveis"
    return label.replace("#", r"\#") if plt.rcParams.get("text.usetex") else label

def _columns_match(table, left, right):
    if left not in table or right not in table:
        return False

    return all(abs(a - b) <= 1e-12 for a, b in zip(table[left], table[right]))

def as_finite_float(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(value):
        return None

    return value

def has_numeric_column(table, column):
    if table is None or column not in table:
        return False

    return any(as_finite_float(value) is not None for value in table[column])

def numeric_values(table, column, cast=float):
    return [cast(value) for value in table[column]]

def finite_values(values):
    return [value for value in values if as_finite_float(value) is not None]

def max_sample_count(table):
    if table is None or "sample_count" not in table:
        return 1

    counts = finite_values(float(value) for value in table["sample_count"])

    if not counts:
        return 1

    return max(int(value) for value in counts)

def plot_value_column(table, base_column):
    mean_column = f"{base_column}_mean"

    if has_numeric_column(table, mean_column):
        return mean_column

    return base_column

def plot_values(table, base_column):
    return numeric_values(table, plot_value_column(table, base_column))

def minimum_values(table, base_column):
    minimum_column = f"{base_column}_min"
    value_column = plot_value_column(table, base_column)

    if not has_numeric_column(table, minimum_column):
        return None
    if _columns_match(table, minimum_column, value_column):
        return None

    return numeric_values(table, minimum_column)

T_CRITICAL_95 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.160,
    14: 2.145,
    15: 2.131,
    16: 2.120,
    17: 2.110,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    21: 2.080,
    22: 2.074,
    23: 2.069,
    24: 2.064,
    25: 2.060,
    26: 2.056,
    27: 2.052,
    28: 2.048,
    29: 2.045,
    30: 2.042,
}

def t_critical_95(sample_count):
    degrees_of_freedom = max(int(sample_count) - 1, 1)

    return T_CRITICAL_95.get(degrees_of_freedom, 1.96)

def confidence_interval_95(table, base_column):
    mean_column = f"{base_column}_mean"
    std_column = f"{base_column}_std"

    if plot_value_column(table, base_column) != mean_column:
        return None
    if "sample_count" not in table or not has_numeric_column(table, std_column):
        return None
    if max_sample_count(table) <= 1:
        return None

    intervals = []

    for std_value, sample_count_value in zip(table[std_column], table["sample_count"]):
        std_value = float(std_value)
        sample_count_value = int(float(sample_count_value))

        if sample_count_value <= 1 or not math.isfinite(std_value):
            intervals.append(0.0)
            continue

        sample_std = std_value * math.sqrt(sample_count_value / (sample_count_value - 1))
        intervals.append(
            t_critical_95(sample_count_value) * sample_std / math.sqrt(sample_count_value)
        )

    return intervals

def plotted_time_statistic(table):
    if has_numeric_column(table, "time_mean") and max_sample_count(table) > 1:
        return "mean"

    for statistic in ("min", "median", "mean"):
        if _columns_match(table, "time", f"time_{statistic}"):
            return statistic

    return "single sample"

def time_axis_label(base, tables):
    tables = [
        table for table in tables
        if table is not None
    ]
    uses_sampled_mean = any(
        has_numeric_column(table, "time_mean") and max_sample_count(table) > 1
        for table in tables
    )
    has_minimum = any(has_numeric_column(table, "time_min") for table in tables)

    if uses_sampled_mean:
        suffix = "mean with 95% CI"

        if has_minimum:
            suffix += "; dashed minimum"

        return f"{base} ({suffix})"

    statistics = {
        plotted_time_statistic(table)
        for table in tables
    }

    if len(statistics) == 1:
        statistic = next(iter(statistics))
    else:
        statistic = "mixed statistics"

    return f"{base} ({statistic})"

def update_bounds(bounds, *series):
    xl, yl, xu, yu = bounds

    for x_values, y_values, yerr in series:
        finite_x = finite_values(x_values)
        finite_y = finite_values(y_values)

        if not finite_x or not finite_y:
            continue

        xl = min(xl, min(finite_x))
        xu = max(xu, max(finite_x))
        yl = min(yl, min(finite_y))

        if yerr is None:
            yu = max(yu, max(finite_y))
        else:
            yu = max(yu, max(y + err for y, err in zip(y_values, yerr)))

    return xl, yl, xu, yu

def plot_metric_series(
    ax,
    table,
    base_column,
    *,
    label,
    marker,
    color=None,
    linestyle="-",
    bounds=None,
):
    n_values = numeric_values(table, "nvar", int)
    y_values = plot_values(table, base_column)
    yerr = confidence_interval_95(table, base_column)
    kwargs = {
        "label": label,
        "marker": marker,
        "linestyle": linestyle,
    }

    if color is not None:
        kwargs["color"] = color

    if yerr is None:
        handle = ax.plot(n_values, y_values, **kwargs)
    else:
        handle = ax.errorbar(n_values, y_values, yerr=yerr, capsize=2.5, **kwargs)

    min_values = minimum_values(table, base_column)

    if min_values is not None:
        min_kwargs = {
            "linestyle": "--",
            "alpha": 0.45,
            "linewidth": 0.9,
        }

        if color is not None:
            min_kwargs["color"] = color

        ax.plot(n_values, min_values, **min_kwargs)

    if bounds is not None:
        bounds = update_bounds(bounds, (n_values, y_values, yerr))

        if min_values is not None:
            bounds = update_bounds(bounds, (n_values, min_values, None))

    if isinstance(handle, list):
        handle = handle[0] if handle else None

    return handle, bounds

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
                elif val == "":
                    table[col].append(float("nan"))
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

        h, bounds = plot_metric_series(
            ax,
            data[tag],
            "time",
            label=label,
            marker=marker,
            color=color,
            linestyle=line,
            bounds=(xl, yl, xu, yu),
        )
        xl, yl, xu, yu = bounds

        if h is not None:
            handles.append(h)

    ax.set_ylim(yl, yu)
    ax.set_xlim(xl, xu)

    if lang == "en":
        ax.set_xlabel(variable_count_label(lang))
        ax.set_ylabel(time_axis_label("Building Time (sec)", data.values()))
    elif lang == "pt":
        ax.set_xlabel(variable_count_label(lang))
        ax.set_ylabel(time_axis_label("Tempo de Montagem (seg)", data.values()))
    ax.grid(True)

    return handles

def plot_toqubo(key: str, ax):
    toqubo_data = maybe_read_csv("ToQUBO", key)
    amplify_data = maybe_read_csv("amplify", key)

    if toqubo_data is not None:
        has_phase_split = "compiler_time" in toqubo_data and "convert_time" in toqubo_data

        plot_metric_series(
            ax,
            toqubo_data,
            "time",
            label="JuMP + ToQUBO",
            marker='*',
        )
        plot_metric_series(
            ax,
            toqubo_data,
            "jump_time",
            label="JuMP",
            marker='D',
        )

        if has_phase_split:
            plot_metric_series(
                ax,
                toqubo_data,
                "compiler_time",
                label="ToQUBO optimize!",
                marker='o',
            )
            plot_metric_series(
                ax,
                toqubo_data,
                "convert_time",
                label="Backend extraction",
                marker='s',
            )
        else:
            plot_metric_series(
                ax,
                toqubo_data,
                "toqubo_time",
                label="ToQUBO",
                marker='D',
            )

    if amplify_data is not None:
        plot_metric_series(
            ax,
            amplify_data,
            "time",
            label="Amplify",
            marker='X',
        )

    if key == "tsp":
        ax.set_xscale('symlog')
        ax.set_yscale('symlog')

    ax.set_xlabel(variable_count_label("en"))
    ax.set_ylabel(time_axis_label(
        "Running Time (sec)",
        [toqubo_data, amplify_data],
    ))
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
