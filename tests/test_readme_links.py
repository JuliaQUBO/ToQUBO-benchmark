from pathlib import Path
import unittest


README = Path(__file__).resolve().parents[1] / "README.md"


class ReadmeLinkTests(unittest.TestCase):
    def setUp(self):
        self.readme = README.read_text(encoding="utf-8")

    def test_uses_juliaqubo_repositories(self):
        self.assertIn("https://github.com/JuliaQUBO/QUBO.jl", self.readme)
        self.assertIn(
            "https://github.com/JuliaQUBO/ToQUBO-benchmark.git",
            self.readme,
        )

    def test_legacy_psr_links_are_removed(self):
        legacy_owner = "psr" + "energy"
        legacy_branch_suffix = ".git" + "#master"

        self.assertNotIn(f"github.com/{legacy_owner}", self.readme)
        self.assertNotIn(f"ToQUBO-benchmark{legacy_branch_suffix}", self.readme)


if __name__ == "__main__":
    unittest.main()
