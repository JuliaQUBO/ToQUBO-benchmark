from __future__ import annotations

import importlib.metadata
from pathlib import Path
import sys
import time
import types
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


from .. import benchmark, tsp_info, npp_info

__DIR__ = Path(__file__).parent


def ensure_pkg_resources():
    """Install a minimal importlib.metadata shim when setuptools >= 82 omits pkg_resources."""
    existing = sys.modules.get("pkg_resources")
    if existing is not None:
        return existing
    try:
        import pkg_resources

        return pkg_resources
    except ModuleNotFoundError:
        pass

    class _Distribution:
        def __init__(self, key: str, version: str):
            self.key = key
            self.project_name = key
            self.version = version

    def get_distribution(dist_name: str) -> _Distribution:
        key = str(dist_name).lower().replace("_", "-")
        return _Distribution(key, importlib.metadata.version(dist_name))

    def _iter_working_set():
        seen = set()
        for dist in importlib.metadata.distributions():
            name = dist.metadata["Name"] if "Name" in dist.metadata else None
            if not name:
                continue
            key = name.lower().replace("_", "-")
            if key in seen:
                continue
            seen.add(key)
            yield _Distribution(key, dist.version)

    shim = types.ModuleType("pkg_resources")
    shim.DistributionNotFound = importlib.metadata.PackageNotFoundError
    shim.get_distribution = get_distribution
    shim.working_set = list(_iter_working_set())
    sys.modules["pkg_resources"] = shim
    return shim


ensure_pkg_resources()


def build_tsp_model(n: int, D: np.ndarray):
    from docplex.mp.model import Model

    model = Model(f"TSP({n})")

    var_matrix = [[model.binary_var(f"x({i},{j})") for j in range(n)] for i in range(n)]

    for i in range(n):
        model.add_constraint(sum(var_matrix[i][:])==1)

    for j in range(n):
        model.add_constraint(sum(var_matrix[:][j])==1)

    distance = []

    for i in range(n):
        for j in range(n):
            for k in range(n):
                distance.append(var_matrix[k][i] * var_matrix[(k+1)%n][j] * D[i, j])

    distance = sum(distance)

    model.minimize(distance)

    return model


def build_npp_model(n: int, s: np.ndarray):
    from docplex.mp.model import Model

    model = Model(f"NPP({n})")

    x = [model.binary_var(f"x({i})") for i in range(n)]

    H = sum((2*x[i]-1) * s[i] for i in range(n))**2

    model.minimize(H)

    return model


def tsp(n: int, D: np.ndarray, lam: float = 5.0):
    t0 = time.time()
    model = build_tsp_model(n, D)

    # Compile Model
    t1 = time.time()

    ensure_pkg_resources()
    from openqaoa.problems.converters import FromDocplex2IsingModel

    ising = FromDocplex2IsingModel(model)

    # Translate to QUBO
    t2 = time.time() 


    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }


def npp(n: int, s: np.ndarray, lam: float = 5.0):

    t0 = time.time()
    model = build_npp_model(n, s)

    # Compile Model
    t1 = time.time()

    ensure_pkg_resources()
    from openqaoa.problems.converters import FromDocplex2IsingModel

    qubo = FromDocplex2IsingModel(model)

    # Translate to QUBO
    t2 = time.time() 


    t3 = time.time()

    return {
        "model_time"    : t1 - t0,
        "compiler_time" : t2 - t1,
        "convert_time"  : t3 - t2,
        "total_time"    : t3 - t0,
    }


if __name__ == "__main__":
    benchmark("tsp", **tsp_info(path=__DIR__, run=tsp, start=5, step=5, stop=100))
    benchmark("npp", **npp_info(path=__DIR__, run=npp, start=20, step=20, stop=1000))
