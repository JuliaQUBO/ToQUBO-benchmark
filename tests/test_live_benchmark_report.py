import csv
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "report.json"


class LiveBenchmarkReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_report_identifies_live_diagnostic_rerun(self):
        self.assertEqual(self.report["schema_version"], 1)
        self.assertEqual(
            self.report["result_set"]["status"],
            "coherent-diagnostic-rerun",
        )
        self.assertEqual(self.report["result_set"]["refs_issue"], 12)
        self.assertIsNone(self.report["result_set"]["closes_issue"])

    def test_report_records_expected_package_versions(self):
        python_packages = self.report["packages"]["python"]
        julia_packages = self.report["packages"]["julia"]

        self.assertEqual(python_packages["qiskit"], "2.4.1")
        self.assertEqual(python_packages["qiskit-optimization"], "0.7.0")
        self.assertIsNone(python_packages["openqaoa"])
        self.assertEqual(julia_packages["ToQUBO"], "0.4.1")
        self.assertEqual(julia_packages["QUBOTools"], "0.13.1")

    def test_report_file_hashes_match_live_csvs(self):
        files = self.report["files"]
        self.assertGreaterEqual(len(files), 10)

        for entry in files:
            with self.subTest(path=entry["path"]):
                path = ROOT / entry["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])

                with path.open(newline="", encoding="utf-8") as csv_file:
                    rows = list(csv.DictReader(csv_file))

                self.assertEqual(len(rows), entry["rows"])
                self.assertEqual(max(int(row["nvar"]) for row in rows), entry["max_nvar"])

    def test_toqubo_extraction_caveat_is_recorded(self):
        extraction = self.report["toqubo_extraction"]

        self.assertEqual(extraction["status"], "internal-backend-access")
        self.assertIn("ToQUBO.qubo", extraction["public_api_check"])
        self.assertGreater(extraction["largest_tsp_convert_share"], 0.9)


if __name__ == "__main__":
    unittest.main()
