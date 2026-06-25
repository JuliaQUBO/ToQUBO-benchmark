import csv
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOQUBO_RESULTS = ROOT / "benchmark" / "ToQUBO"


class ToQUBOResultTests(unittest.TestCase):
    def test_phase_split_columns_are_present_and_consistent(self):
        expected_fields = [
            "nvar",
            "time",
            "jump_time",
            "toqubo_time",
            "compiler_time",
            "convert_time",
        ]

        for key in ("tsp", "npp"):
            with self.subTest(problem=key):
                path = TOQUBO_RESULTS / f"results.{key}.csv"

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


if __name__ == "__main__":
    unittest.main()
