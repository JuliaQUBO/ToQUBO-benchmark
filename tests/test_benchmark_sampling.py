import csv
from pathlib import Path
import tempfile
import unittest

from benchmark import benchmark, summarize_samples


class BenchmarkSamplingTests(unittest.TestCase):
    def test_summarize_samples_records_min_median_mean_and_counts(self):
        summary = summarize_samples(
            [
                {"model_time": 2.0, "convert_time": 1.0, "total_time": 3.0},
                {"model_time": 1.0, "convert_time": 0.5, "total_time": 1.5},
                {"model_time": 4.0, "convert_time": 2.0, "total_time": 6.0},
            ],
            samples_run=3,
            warmups_run=1,
            statistic="min",
        )

        self.assertEqual(summary["time"], 1.5)
        self.assertEqual(summary["time_min"], 1.5)
        self.assertEqual(summary["time_median"], 3.0)
        self.assertEqual(summary["time_mean"], 3.5)
        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["warmup_count"], 1)
        self.assertEqual(summary["model_time"], 1.0)
        self.assertEqual(summary["convert_time_median"], 1.0)

    def test_benchmark_writes_sampled_phase_columns(self):
        calls = []

        def run(n, data):
            calls.append((n, data))
            value = float(len(calls))

            return {
                "model_time": value,
                "convert_time": value / 10.0,
                "total_time": value + 0.25,
            }

        with tempfile.TemporaryDirectory() as tmpdir:
            benchmark(
                "npp",
                path=tmpdir,
                run=run,
                data=lambda n: n * 2,
                nvar=lambda n: n,
                start=1,
                step=1,
                stop=1,
                samples=2,
                warmups=1,
                statistic="min",
            )

            path = Path(tmpdir) / "results.npp.csv"
            with path.open(newline="", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                rows = list(reader)

        self.assertEqual(len(calls), 3)
        self.assertEqual(len(rows), 1)
        self.assertIn("model_time", reader.fieldnames)
        self.assertIn("convert_time_median", reader.fieldnames)
        self.assertEqual(rows[0]["sample_count"], "2")
        self.assertEqual(rows[0]["warmup_count"], "1")
        self.assertEqual(float(rows[0]["time"]), 2.25)
        self.assertEqual(float(rows[0]["time_median"]), 2.75)


if __name__ == "__main__":
    unittest.main()
