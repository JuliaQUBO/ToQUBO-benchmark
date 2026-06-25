import importlib
import unittest


class OpenQAOABenchmarkTests(unittest.TestCase):
    def test_tsp_model_sets_distance_objective(self):
        try:
            import numpy as np
            openqaoa_benchmark = importlib.import_module("benchmark.openqaoa.__main__")
            importlib.import_module("docplex.mp.model")
        except ImportError as exc:
            self.skipTest(f"OpenQAOA benchmark dependency is not installed: {exc}")

        distance = np.array(
            [
                [0, 1, 2],
                [1, 0, 3],
                [2, 3, 0],
            ]
        )

        model = openqaoa_benchmark.build_tsp_model(3, distance)

        self.assertNotEqual(str(model.objective_expr), "0")
