import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"web/reviews/odyssee-p7-round2.html"
DIST=ROOT/"dist/reviews/odyssee-p7-round2.html"
HUMAN=ROOT/"series/odyssee/review/P7_ROUND2_HUMAN_REVIEW_V1.json"
HANDOFF=ROOT/"series/odyssee/production/STREAM3_HANDOFF_V1.json"
H2=ROOT/"series/odyssee/review/H2_SINGLE_BATCH_REVIEW_V1.json"

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


    def test_frozen_product_authority_routes_ulysse_to_179_and_telemaque_to_178(self):
        human=json.loads(HUMAN.read_text(encoding="utf-8"))
        arbitration=human["frozen_stream1_arbitration"]
        self.assertEqual(arbitration["final_p7_ulysse_conclusion"],"P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER")
        self.assertEqual(arbitration["ulysse_lane_issue"],179)
        self.assertEqual(arbitration["telemaque_defect_issue"],178)
        self.assertFalse(arbitration["telemaque_blocks_p7_ulysse_conclusion"])
        self.assertTrue(arbitration["edge_artistic_budget_exhausted"])
        self.assertTrue(arbitration["no_round3_edge"])
        self.assertFalse(arbitration["recasting_authorized"])
        self.assertFalse(arbitration["frozen_text_change_authorized"])

    def test_handoff_keeps_telemaque_orthogonal_to_p7_conclusion(self):
        handoff=json.loads(HANDOFF.read_text(encoding="utf-8"))
        p7=handoff["qa"]["p7_ulysse_performance_continuity"]
        telemaque=handoff["qa"]["telemaque_language_integrity"]
        self.assertEqual(p7["state"],"P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER")
        self.assertEqual(p7["new_ulysse_lane_issue"],179)
        self.assertEqual(p7["telemaque_separate_defect_issue"],178)
        self.assertFalse(p7["telemaque_blocks_p7_ulysse_conclusion"])
        self.assertTrue(p7["no_round3_edge"])
        self.assertEqual(telemaque["relation_to_p7_ulysse"],"ORTHOGONAL")

    def test_h2_remains_suspended_on_two_independent_open_lanes(self):
        h2=json.loads(H2.read_text(encoding="utf-8"))
        self.assertEqual(h2["status"],"H2_SUSPENDED_ULYSSE_PROVIDER_AND_TELEMAQUE_INTEGRITY")
        self.assertEqual(h2["suspension"]["ulysses_performance"]["issue"],179)
        self.assertEqual(h2["suspension"]["telemaque_language_integrity"]["issue"],178)
        self.assertFalse(h2["suspension"]["telemaque_language_integrity"]["blocks_p7_ulysse_conclusion"])

    def test_static_build_publishes_round2_page(self):
        subprocess.run([sys.executable,"site/build.py"],cwd=ROOT,check=True)
        self.assertTrue(DIST.is_file())

if __name__=="__main__":
    unittest.main()
