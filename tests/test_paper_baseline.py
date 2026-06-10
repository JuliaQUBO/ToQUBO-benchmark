import csv
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "archive" / "paper-v1"
MANIFEST = BASELINE / "manifest.json"


class PaperBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_identifies_paper_baseline(self):
        self.assertEqual(self.manifest["baseline_id"], "paper-v1")
        self.assertEqual(self.manifest["paper"]["arxiv"], "2307.02577")
        self.assertEqual(self.manifest["source"]["report_time"], "2023-05-14 23:16:20.211039")
        self.assertEqual(self.manifest["environment"]["python"], "CPython version 3.10.6")
        self.assertEqual(self.manifest["environment"]["julia"], "1.9.0")

    def test_archived_files_match_manifest_hashes(self):
        files = self.manifest["files"]

        self.assertEqual(len(files), 15)

        for entry in files:
            with self.subTest(path=entry["path"]):
                path = BASELINE / entry["path"]

                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])

    def test_archived_csvs_have_expected_shape(self):
        for entry in self.manifest["files"]:
            if not entry["path"].endswith(".csv"):
                continue

            with self.subTest(path=entry["path"]):
                path = BASELINE / entry["path"]

                with path.open(newline="", encoding="utf-8") as csv_file:
                    reader = csv.DictReader(csv_file)
                    rows = list(reader)

                self.assertIn("nvar", reader.fieldnames)
                self.assertIn("time", reader.fieldnames)
                self.assertGreater(len(rows), 0)

    def test_report_matches_manifest(self):
        report = json.loads((BASELINE / "data" / "report.json").read_text(encoding="utf-8"))

        self.assertEqual(report["time"], self.manifest["source"]["report_time"])
        self.assertEqual(report["python"], self.manifest["environment"]["python"])
        self.assertEqual(report["julia"], f"julia version {self.manifest['environment']['julia']}")
        self.assertEqual(report["cpuinfo"]["brand_raw"], self.manifest["environment"]["cpu"])


if __name__ == "__main__":
    unittest.main()
