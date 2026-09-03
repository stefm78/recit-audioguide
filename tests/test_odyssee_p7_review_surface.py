import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"series/odyssee/review/P7_ULYSSE_PERFORMANCE_CONTINUITY_V1.json"
PAGE=ROOT/"web/reviews/odyssee-p7.html"
DESCRIPTOR=ROOT/"web/reviews/data/odyssee-p7-round1-203a196-v1.json"
DIST=ROOT/"dist/reviews/odyssee-p7.html"
DIST_DESCRIPTOR=ROOT/"dist/reviews/data/odyssee-p7-round1-203a196-v1.json"

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

    def test_page_autoloads_release_tag_from_query(self):
        text=PAGE.read_text(encoding="utf-8")
        self.assertIn('new URLSearchParams(window.location.search).get("tag")',text)
        self.assertIn("if(initialTag)",text)
        self.assertIn("load()",text)

    def test_page_uses_same_origin_release_descriptor_not_github_api(self):
        text=PAGE.read_text(encoding="utf-8")
        self.assertIn('var DESCRIPTOR_BASE="data/"',text)
        self.assertIn('DESCRIPTOR_BASE+encodeURIComponent(tag)+".json"',text)
        self.assertNotIn("api.github.com",text)
        descriptor=json.loads(DESCRIPTOR.read_text(encoding="utf-8"))
        self.assertEqual(descriptor["tag"],"odyssee-p7-round1-203a196-v1")
        self.assertEqual(descriptor["status"],"machine-ready-p7-review-assets")
        self.assertEqual(descriptor["asset_count"],17)
        self.assertEqual(len(descriptor["assets"]),17)

    def test_build_publishes_page(self):
        subprocess.run([sys.executable,"site/build.py"],cwd=ROOT,check=True)
        self.assertTrue(DIST.is_file())
        self.assertTrue(DIST_DESCRIPTOR.is_file())

if __name__=="__main__": unittest.main()
