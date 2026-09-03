import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-h2.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-h2.html"
CONTRACT = ROOT / "series" / "odyssee" / "review" / "H2_SINGLE_BATCH_REVIEW_V1.json"

REQUIRED_ASSETS = [
    "review-index.json",
    "block-A.mp3", "block-A.qa-report.json",
    "block-B.mp3", "block-B.qa-report.json",
    "block-C.mp3", "block-C.qa-report.json",
    "block-D.mp3", "block-D.qa-report.json",
    "scene-S09.mp3", "scene-S09.qa-report.json",
    "scene-S13.mp3", "scene-S13.qa-report.json",
    "scene-S14.mp3", "scene-S14.qa-report.json",
    "scene-S15.mp3", "scene-S15.qa-report.json",
]

class OdysseeH2ReviewSurfaceTests(unittest.TestCase):
    def test_contract_is_single_batch_and_fail_closed(self):
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "H2_SUSPENDED_P7_ULYSSE_PERFORMANCE_CONTINUITY")
        self.assertEqual(data["entry_gate"]["exact_confirmation"], "A+B+C+D MACHINE_QUALIFIED")
        self.assertEqual(data["entry_gate"]["additional_artistic_gate"], "P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS")
        self.assertTrue(data["entry_gate"]["fail_closed"])
        self.assertTrue(data["review_surface"]["one_batch"])
        self.assertTrue(data["review_surface"]["micro_reviews_forbidden"])
        self.assertEqual(data["decision"]["pass"], "PASS_H2_SINGLE_BATCH")
        self.assertEqual(data["decision"]["fail"], "FAIL_H2_TARGETED_CORRECTION")
        self.assertTrue(data["review_semantics"]["observation_is_not_verdict"])

    def test_contract_covers_real_integrated_work(self):
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        ids = {item["id"] for item in data["ordered_modules"]}
        self.assertTrue({
            "block-a", "block-b", "s09", "b-to-c", "c-to-d",
            "s13", "s14", "s15", "global-comparison"
        }.issubset(ids))
        criteria = {item["id"] for item in data["criteria"]}
        self.assertTrue({
            "pacing_comprehension", "listening_fatigue", "identity_coherence",
            "marin_context", "p5_integration", "p4_s09_integration",
            "block_transitions", "climax_build", "s15_climax",
            "global_dynamics", "sound_density_silence",
            "interblock_levels", "audible_technical_defects"
        }.issubset(criteria))

    def test_page_requires_complete_machine_qualified_release(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("A+B+C+D MACHINE_QUALIFIED", text)
        self.assertIn("P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS", text)
        self.assertIn('var P7_GATE="PENDING"', text)
        self.assertIn("Release partielle — ce n’est pas H2.", text)
        for asset in REQUIRED_ASSETS:
            self.assertIn(asset, text)

    def test_page_separates_observation_from_artistic_verdict(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("Observation perceptive", text)
        self.assertIn("Verdict artistique", text)
        self.assertIn("PRESENT / ABSENT / LIGHT / STRONG ne sont jamais des verdicts", text)
        self.assertIn("PASS_H2_SINGLE_BATCH", text)
        self.assertIn("FAIL_H2_TARGETED_CORRECTION", text)
        self.assertIn("Copier le bilan", text)

    def test_page_contains_no_capability_micro_review(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("Ce n’est pas une recertification de capability.", text)
        self.assertIn("Les 12 vraies lignes Ulysse", text)
        self.assertIn("no micro-review", text)
        self.assertNotIn("DÉCISION P4", text)
        self.assertNotIn("DÉCISION P6", text)

    def test_static_build_publishes_h2_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn("Odyssée — H2 final partagé", built)
        self.assertIn("review-index.json", built)

if __name__ == "__main__":
    unittest.main()
