import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"series/odyssee/review/P7_ULYSSE_PERFORMANCE_CONTINUITY_V1.json"
PAGE=ROOT/"web/reviews/odyssee-p7.html"
DIST=ROOT/"dist/reviews/odyssee-p7.html"

class P7Tests(unittest.TestCase):
    def test_scope_and_stop_rule(self):
        data=json.loads(SPEC.read_text(encoding="utf-8"))
        self.assertEqual(data["status"],"P7_READY_FOR_STREAM3_RENDER")
        self.assertFalse(data["constraints"]["recasting"])
        self.assertFalse(data["constraints"]["frozen_text_change"])
        self.assertEqual(data["constraints"]["voice"],"fr-FR-HenriNeural")
        self.assertEqual(len(data["round_1"]["windows"]),4)
        self.assertEqual(data["decision"]["bounded_retry"]["max_additional_rounds"],1)
        self.assertEqual(data["decision"]["pass"],"P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS")

    def test_exact_windows_are_guarded(self):
        data=json.loads(SPEC.read_text(encoding="utf-8"))
        for w in data["round_1"]["windows"]:
            start=w["range"]["start_segment"]; end=w["range"]["end_segment"]
            self.assertEqual(len(w["exact_guards"]),end-start+1)
            self.assertTrue(all(g["segment"]>=start and g["segment"]<=end for g in w["exact_guards"]))
            self.assertTrue(all(x in [g["segment"] for g in w["exact_guards"]] for x in w["ulysse_segments"]))

    def test_page_keeps_observation_separate(self):
        text=PAGE.read_text(encoding="utf-8")
        self.assertIn("Observation perceptive",text)
        self.assertIn("P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS",text)
        self.assertIn("P7_EDGE_BOUNDED_RETUNE_REQUIRED",text)
        self.assertIn("identité Henri préservée",text)

    def test_build_publishes_page(self):
        subprocess.run([sys.executable,"site/build.py"],cwd=ROOT,check=True)
        self.assertTrue(DIST.is_file())

if __name__=="__main__": unittest.main()
