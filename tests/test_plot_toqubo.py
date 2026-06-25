import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PLOT_MODULE = ROOT / "plot" / "plot.py"


class FakeFrame:
    def __init__(self):
        self.facecolor = None

    def set_facecolor(self, value):
        self.facecolor = value


class FakeLegend:
    def __init__(self):
        self.frame = FakeFrame()

    def get_frame(self):
        return self.frame


class FakeAxis:
    def __init__(self):
        self.labels = []
        self.xscale = None
        self.yscale = None
        self.legend_calls = 0

    def plot(self, *args, **kwargs):
        label = kwargs.get("label")
        if label is not None:
            self.labels.append(label)
        return []

    def set_xscale(self, value):
        self.xscale = value

    def set_yscale(self, value):
        self.yscale = value

    def set_xlabel(self, value):
        pass

    def set_ylabel(self, value):
        pass

    def grid(self, value):
        pass

    def get_legend_handles_labels(self):
        return [object() for _ in self.labels], list(self.labels)

    def legend(self, *args, **kwargs):
        self.legend_calls += 1
        return FakeLegend()


def load_plot_module():
    matplotlib = types.ModuleType("matplotlib")
    pyplot = types.ModuleType("matplotlib.pyplot")
    pyplot.rcParams = {}
    scienceplots = types.ModuleType("scienceplots")
    numpy = types.ModuleType("numpy")
    scipy = types.ModuleType("scipy")
    scipy_optimize = types.ModuleType("scipy.optimize")
    scipy_optimize.curve_fit = lambda *args, **kwargs: None

    modules = {
        "matplotlib": matplotlib,
        "matplotlib.pyplot": pyplot,
        "scienceplots": scienceplots,
        "numpy": numpy,
        "scipy": scipy,
        "scipy.optimize": scipy_optimize,
    }

    with mock.patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location("plot_under_test", PLOT_MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    return module


class PlotToQUBOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plot_module = load_plot_module()

    def test_phase_split_plot_handles_missing_amplify(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            toqubo_path = base_path / "ToQUBO"
            toqubo_path.mkdir()
            (toqubo_path / "results.tsp.csv").write_text(
                "nvar,time,jump_time,toqubo_time,compiler_time,convert_time\n"
                "4,1.0,0.2,0.8,0.3,0.5\n",
                encoding="utf-8",
            )

            self.plot_module.BASE_PATH = base_path
            ax = FakeAxis()

            self.plot_module.plot_toqubo("tsp", ax)

        self.assertEqual(
            ax.labels,
            ["JuMP + ToQUBO", "JuMP", "ToQUBO optimize!", "Backend extraction"],
        )
        self.assertEqual(ax.xscale, "symlog")
        self.assertEqual(ax.yscale, "symlog")
        self.assertEqual(ax.legend_calls, 1)

    def test_plot_handles_missing_toqubo_with_amplify_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            amplify_path = base_path / "amplify"
            amplify_path.mkdir()
            (amplify_path / "results.npp.csv").write_text(
                "nvar,time\n"
                "4,1.0\n",
                encoding="utf-8",
            )

            self.plot_module.BASE_PATH = base_path
            ax = FakeAxis()

            self.plot_module.plot_toqubo("npp", ax)

        self.assertEqual(ax.labels, ["Amplify"])
        self.assertIsNone(ax.xscale)
        self.assertIsNone(ax.yscale)
        self.assertEqual(ax.legend_calls, 1)

    def test_variable_count_label_escapes_latex_hash(self):
        self.plot_module.plt.rcParams["text.usetex"] = True

        self.assertEqual(self.plot_module.variable_count_label("en"), r"\#variables")
        self.assertEqual(self.plot_module.variable_count_label("pt"), r"\#variaveis")

        self.plot_module.plt.rcParams["text.usetex"] = False

        self.assertEqual(self.plot_module.variable_count_label("en"), "#variables")

    def test_read_csv_handles_blank_optional_metric_cells(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "results.npp.csv"
            path.write_text(
                "nvar,time,model_time\n"
                "1,0.1,\n",
                encoding="utf-8",
            )

            table = self.plot_module.read_csv(path)

        self.assertEqual(table["nvar"], [1])
        self.assertEqual(table["time"], [0.1])
        self.assertTrue(math.isnan(table["model_time"][0]))


if __name__ == "__main__":
    unittest.main()
