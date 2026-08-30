import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-p4v2-casting.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-p4v2-casting.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-p4v2-casting-review-v1"
SOURCE = "508c1e4248ee2680cc0c92feef2c64b4bd1ba06f"
A_SHA = "ce60ef91547f1867135f0702a23e1bbb80faab5da9cfe47a491b2dc75aeb7f88"
B_SHA = "c94745117fa3dd710c8d456980c5783d8a2dcf19083698e5a2a8b79ab79b9307"

class OdysseeP4V2CastingReviewSurfaceTests(unittest.TestCase):
    def test_review_page_is_bound_to_two_immutable_assets(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/denise-directe.mp3", text)
        self.assertIn(f"{RELEASE}/denise-retenue.mp3", text)
        self.assertIn(SOURCE, text)
        self.assertIn(A_SHA, text)
        self.assertIn(B_SHA, text)
        self.assertIn("Candidate A", text)
        self.assertIn("Candidate B", text)
        self.assertIn("PASS CASTING", text)
        self.assertIn("FAIL CASTING", text)
        self.assertIn("Copier le bilan", text)
        self.assertNotIn("download=", text.lower())

    def test_static_build_publishes_casting_page_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/denise-directe.mp3", built)
        self.assertIn("Aucun fichier à exporter", built)

if __name__ == "__main__":
    unittest.main()
