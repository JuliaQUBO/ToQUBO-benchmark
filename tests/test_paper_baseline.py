import csv
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "archive" / "paper-v1"
MANIFEST = BASELINE / "manifest.json"
PUBLICATION_BASELINE = ROOT / "archive" / "publication-10-sample-2026-06-25"
PUBLICATION_MANIFEST = PUBLICATION_BASELINE / "manifest.json"


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


class PublicationBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(PUBLICATION_MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_identifies_publication_baseline(self):
        self.assertEqual(self.manifest["baseline_id"], "publication-10-sample-2026-06-25")
        self.assertEqual(
            self.manifest["source"]["result_set_id"],
            "publication-10-sample-full-2026-06-25",
        )
        self.assertEqual(self.manifest["source"]["results_commit"], "1d1bf06145a2a0e0c9859713ccfb8a35458efc8f")
        self.assertEqual(self.manifest["source"]["documented_commit"], "d773d7eb0f4331c38e8e44e671ae4c11f1a799e6")
        self.assertEqual(self.manifest["methodology"]["sample_count"], 10)
        self.assertEqual(self.manifest["methodology"]["warmup_count"], 1)
        self.assertEqual(self.manifest["methodology"]["time_statistic"], "min")

    def test_archived_files_match_manifest_hashes(self):
        files = self.manifest["files"]

        self.assertEqual(len(files), 27)

        for entry in files:
            with self.subTest(path=entry["path"]):
                path = PUBLICATION_BASELINE / entry["path"]

                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])

    def test_archived_csvs_record_publication_sampling(self):
        for entry in self.manifest["files"]:
            if not entry["path"].endswith(".csv"):
                continue

            with self.subTest(path=entry["path"]):
                path = PUBLICATION_BASELINE / entry["path"]

                with path.open(newline="", encoding="utf-8") as csv_file:
                    reader = csv.DictReader(csv_file)
                    rows = list(reader)

                self.assertIn("nvar", reader.fieldnames)
                self.assertIn("time", reader.fieldnames)
                self.assertIn("time_mean", reader.fieldnames)
                self.assertIn("time_min", reader.fieldnames)
                self.assertIn("sample_count", reader.fieldnames)
                self.assertIn("warmup_count", reader.fieldnames)
                self.assertGreater(len(rows), 0)
                self.assertEqual({int(float(row["sample_count"])) for row in rows}, {10})
                self.assertEqual({int(float(row["warmup_count"])) for row in rows}, {1})

    def test_report_matches_manifest(self):
        report = json.loads(
            (PUBLICATION_BASELINE / "data" / "report.json").read_text(encoding="utf-8")
        )

        self.assertEqual(report["result_set"]["id"], self.manifest["source"]["result_set_id"])
        self.assertEqual(report["generated_at"], self.manifest["source"]["report_generated_at"])
        self.assertEqual(report["benchmark_methodology"], self.manifest["methodology"])
        self.assertEqual(report["environment"], self.manifest["environment"])
        self.assertEqual(report["packages"], self.manifest["packages"])
        self.assertEqual(report["toqubo_extraction"], self.manifest["toqubo_extraction"])


if __name__ == "__main__":
    unittest.main()
