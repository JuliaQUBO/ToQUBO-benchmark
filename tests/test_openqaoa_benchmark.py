import builtins
import importlib
import sys
import unittest


class OpenQAOABenchmarkTests(unittest.TestCase):
    def test_ensure_pkg_resources_installs_importlib_metadata_shim_when_missing(self):
        openqaoa_benchmark = importlib.import_module("benchmark.openqaoa.__main__")
        saved_module = sys.modules.get("pkg_resources")
        real_import = builtins.__import__

        def blocked_pkg_resources_import(name, *args, **kwargs):
            if name == "pkg_resources":
                raise ModuleNotFoundError("No module named 'pkg_resources'")
            return real_import(name, *args, **kwargs)

        try:
            sys.modules.pop("pkg_resources", None)
            builtins.__import__ = blocked_pkg_resources_import
            shim = openqaoa_benchmark.ensure_pkg_resources()
            self.assertIs(sys.modules.get("pkg_resources"), shim)
            self.assertTrue(hasattr(shim, "get_distribution"))
            self.assertTrue(hasattr(shim, "working_set"))
            self.assertTrue(hasattr(shim, "DistributionNotFound"))
            with self.assertRaises(shim.DistributionNotFound):
                shim.get_distribution("nonexistent-package-for-toqubo-benchmark-test")
        finally:
            builtins.__import__ = real_import
            if saved_module is not None:
                sys.modules["pkg_resources"] = saved_module
            else:
                sys.modules.pop("pkg_resources", None)

    def test_tsp_and_npp_succeed_with_pkg_resources_shim(self):
        try:
            import numpy as np
            openqaoa_benchmark = importlib.import_module("benchmark.openqaoa.__main__")
            importlib.import_module("docplex.mp.model")
            importlib.import_module("openqaoa")
        except ImportError as exc:
            self.skipTest(f"OpenQAOA benchmark dependency is not installed: {exc}")

        saved_pkg_resources = sys.modules.get("pkg_resources")
        real_import = builtins.__import__

        def blocked_pkg_resources_import(name, *args, **kwargs):
            if name == "pkg_resources" and "pkg_resources" not in sys.modules:
                raise ModuleNotFoundError("No module named 'pkg_resources'")
            return real_import(name, *args, **kwargs)

        try:
            for mod_name in [
                k for k in list(sys.modules)
                if k == "pkg_resources" or k.startswith(("openqaoa", "qiskit_ibm_provider"))
            ]:
                sys.modules.pop(mod_name, None)
            builtins.__import__ = blocked_pkg_resources_import

            distance = np.array(
                [
                    [0, 1, 2],
                    [1, 0, 3],
                    [2, 3, 0],
                ]
            )
            tsp_metrics = openqaoa_benchmark.tsp(3, distance)
            self.assertIn("total_time", tsp_metrics)

            numbers = np.array([1, 2, 3])
            npp_metrics = openqaoa_benchmark.npp(3, numbers)
            self.assertIn("total_time", npp_metrics)
        finally:
            builtins.__import__ = real_import
            if saved_pkg_resources is not None:
                sys.modules["pkg_resources"] = saved_pkg_resources

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
