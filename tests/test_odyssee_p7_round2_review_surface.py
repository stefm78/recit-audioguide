import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"web/reviews/odyssee-p7-round2.html"
DIST=ROOT/"dist/reviews/odyssee-p7-round2.html"

class P7Round2ReviewSurfaceTests(unittest.TestCase):
    def test_page_is_fixed_to_final_round2_release(self):
        text=PAGE.read_text(encoding="utf-8")
        self.assertIn('var R1="odyssee-p7-round1-203a196-v1"',text)
        self.assertIn('var EXPECTED_R2="odyssee-p7-round2-line-microprosody-v1"',text)
        self.assertNotIn("api.github.com",text)

    def test_page_compares_round1_b_to_round2_c(self):
        text=PAGE.read_text(encoding="utf-8")
        self.assertIn("B1 — Round 1 rejeté",text)
        self.assertIn("C2 — micro-prosodie",text)
        self.assertIn("p7-r2-",text)

    def test_page_has_probe_integrity_branch(self):
        text=PAGE.read_text(encoding="utf-8")
        self.assertIn("P7_ROUND2_PROBE_INTEGRITY_FAIL",text)
        self.assertIn("Contexte linguistique techniquement propre",text)

    def test_page_has_final_edge_decisions(self):
        text=PAGE.read_text(encoding="utf-8")
        self.assertIn("P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS",text)
        self.assertIn("P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER",text)
        self.assertIn("Aucun Round 3 Edge",text)
        self.assertIn("edge_budget_exhausted:true",text)
        self.assertIn("technical integrity decision does not reopen",text)

    def test_static_build_publishes_round2_page(self):
        subprocess.run([sys.executable,"site/build.py"],cwd=ROOT,check=True)
        self.assertTrue(DIST.is_file())

if __name__=="__main__":
    unittest.main()
