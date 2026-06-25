import csv
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOQUBO_RESULTS = ROOT / "benchmark" / "ToQUBO"


class ToQUBOResultTests(unittest.TestCase):
    def assert_phase_split_file_is_consistent(self, path):
        expected_fields = [
            "nvar",
            "time",
            "jump_time",
            "toqubo_time",
            "compiler_time",
            "convert_time",
        ]

        with path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            rows = list(reader)

        self.assertEqual(reader.fieldnames[: len(expected_fields)], expected_fields)
        self.assertGreater(len(rows), 0)

        for row in rows:
            toqubo_time = float(row["toqubo_time"])
            compiler_time = float(row["compiler_time"])
            convert_time = float(row["convert_time"])

            if "sample_count" in reader.fieldnames:
                self.assertGreaterEqual(int(row["sample_count"]), 1)
                self.assertGreaterEqual(int(row["warmup_count"]), 0)
                self.assertIn("time_min", reader.fieldnames)
                self.assertIn("time_median", reader.fieldnames)
                self.assertAlmostEqual(
                    float(row["toqubo_time_mean"]),
                    float(row["compiler_time_mean"]) + float(row["convert_time_mean"]),
                )
            else:
                self.assertAlmostEqual(toqubo_time, compiler_time + convert_time)

    def test_phase_split_columns_are_present_and_consistent(self):
        for key in ("tsp", "npp"):
            with self.subTest(problem=key):
                path = TOQUBO_RESULTS / f"results.{key}.csv"

                self.assert_phase_split_file_is_consistent(path)

    def test_sampled_phase_split_columns_are_consistent(self):
        with self.subTest(problem="sampled-fixture"):
            with tempfile.TemporaryDirectory() as tmpdir:
                path = Path(tmpdir) / "results.npp.csv"
                path.write_text(
                    "nvar,time,jump_time,toqubo_time,compiler_time,convert_time,"
                    "time_min,time_median,time_mean,time_std,"
                    "jump_time_min,jump_time_median,jump_time_mean,jump_time_std,"
                    "toqubo_time_min,toqubo_time_median,toqubo_time_mean,toqubo_time_std,"
                    "compiler_time_min,compiler_time_median,compiler_time_mean,compiler_time_std,"
                    "convert_time_min,convert_time_median,convert_time_mean,convert_time_std,"
                    "sample_count,warmup_count\n"
                    "4,1.0,0.3,0.7,0.4,0.3,"
                    "1.0,1.2,1.1,0.1,"
                    "0.3,0.4,0.35,0.05,"
                    "0.7,0.9,0.8,0.1,"
                    "0.4,0.5,0.45,0.05,"
                    "0.3,0.4,0.35,0.05,"
                    "2,1\n",
                    encoding="utf-8",
                )

                self.assert_phase_split_file_is_consistent(path)


if __name__ == "__main__":
    unittest.main()
