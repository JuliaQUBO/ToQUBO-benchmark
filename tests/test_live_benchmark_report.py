import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "report.json"
REPORT_SCRIPT = ROOT / "scripts" / "write_benchmark_report.py"


def load_report_script():
    spec = importlib.util.spec_from_file_location("write_benchmark_report", REPORT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LiveBenchmarkReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_report_identifies_live_diagnostic_rerun(self):
        self.assertEqual(self.report["schema_version"], 1)
        self.assertEqual(
            self.report["result_set"]["status"],
            "toqubo-0.5.1-rerun",
        )
        self.assertEqual(self.report["result_set"]["refs_issue"], 12)
        self.assertIsNone(self.report["result_set"]["closes_issue"])
        self.assertEqual(
            self.report["result_set"]["toqubo_dependencies"]["status"],
            "registered-release",
        )

    def test_report_records_expected_package_versions(self):
        python_packages = self.report["packages"]["python"]
        julia_packages = self.report["packages"]["julia"]

        self.assertEqual(python_packages["qiskit"], "2.4.1")
        self.assertEqual(python_packages["qiskit-optimization"], "0.7.0")
        self.assertIsNone(python_packages["openqaoa"])
        self.assertEqual(julia_packages["ToQUBO"], "0.5.1")
        self.assertEqual(julia_packages["QUBOTools"], "0.15.1")

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

        self.assertEqual(extraction["status"], "public-backend-api")
        self.assertIn("QUBOTools.backend(model)", extraction["public_api_check"])
        self.assertLess(extraction["largest_tsp_convert_share"], 0.1)

    def test_julia_runtime_uses_report_environment(self):
        report_script = load_report_script()

        with mock.patch.dict(
            report_script.os.environ,
            {
                "BENCHMARK_JULIA": "/opt/julia/bin/julia",
                "BENCHMARK_JULIA_VERSION": "julia version 9.9.9",
            },
            clear=False,
        ):
            runtime = report_script.julia_runtime()

        self.assertEqual(runtime["executable"], "/opt/julia/bin/julia")
        self.assertEqual(runtime["version"], "julia version 9.9.9")

    def test_julia_runtime_queries_executable_when_env_version_is_absent(self):
        report_script = load_report_script()
        completed = subprocess.CompletedProcess(
            ["/opt/julia/bin/julia", "--version"],
            0,
            stdout="julia version 8.8.8\n",
            stderr="",
        )

        with mock.patch.dict(
            report_script.os.environ,
            {"BENCHMARK_JULIA": "/opt/julia/bin/julia"},
            clear=True,
        ), mock.patch.object(report_script.subprocess, "run", return_value=completed) as run:
            runtime = report_script.julia_runtime()

        run.assert_called_once_with(
            ["/opt/julia/bin/julia", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(runtime["version"], "julia version 8.8.8")

    def test_toqubo_extraction_summary_handles_missing_phase_split(self):
        report_script = load_report_script()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "results.tsp.csv"
            path.write_text(
                "nvar,time,jump_time,toqubo_time\n"
                "25,1.0,0.2,0.8\n"
                "100,2.0,0.3,1.7\n",
                encoding="utf-8",
            )

            extraction = report_script.toqubo_extraction_summary(path)

        self.assertEqual(extraction["status"], "phase-split-unavailable")
        self.assertEqual(extraction["largest_tsp_nvar"], 100)
        self.assertEqual(extraction["largest_tsp_toqubo_time"], 1.7)


if __name__ == "__main__":
    unittest.main()
