import csv
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import run_python_benchmark_isolated as runner


class PublicationRunnerTests(unittest.TestCase):
    def test_resume_stops_at_checkpointed_threshold_row(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            results_dir = root / "benchmark" / "pkg"
            results_dir.mkdir(parents=True)
            results_path = results_dir / "results.problem.csv"

            with results_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=["nvar", "time", "sample_count", "warmup_count"],
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerow({"nvar": 1, "time": 1.0, "sample_count": 10, "warmup_count": 1})
                writer.writerow({"nvar": 2, "time": 6.0, "sample_count": 10, "warmup_count": 1})
                writer.writerow({"nvar": 3, "time": 7.0, "sample_count": 10, "warmup_count": 1})

            def run(*_):
                raise AssertionError("runner should stop at the checkpointed threshold row")

            config = {
                "data": lambda n: n,
                "nvar": lambda n: n,
                "start": 1,
                "step": 1,
                "stop": 3,
                "time_limit": 5.0,
            }

            with (
                mock.patch.object(runner, "ROOT", root),
                mock.patch.object(runner, "import_run_function", return_value=run),
                mock.patch.dict(
                    "os.environ",
                    {
                        "BENCHMARK_SAMPLES": "10",
                        "BENCHMARK_WARMUPS": "1",
                        "BENCHMARK_TIME_STATISTIC": "min",
                    },
                ),
            ):
                runner.benchmark_problem("pkg", "module", "problem", config)

            with results_path.open(newline="", encoding="utf-8") as csv_file:
                rows = list(csv.DictReader(csv_file))

        self.assertEqual([row["nvar"] for row in rows], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
