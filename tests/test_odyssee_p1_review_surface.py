import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-p1.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-p1.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-p1-review-v1"
CANDIDATE = "5b9eeca0977f252e588d64545b2b464e9aa3ca4d"
AUDIO_SHA = "b3c9629b920e31033c6aab7b6625d30d29d5c219d3458dfbb3f6a92e4949a5ea"

class OdysseeP1ReviewSurfaceTests(unittest.TestCase):
    def test_review_page_is_bound_to_durable_release(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p1.mp3", text)
        self.assertIn(CANDIDATE, text)
        self.assertIn(AUDIO_SHA, text)
        self.assertIn("Bilan à copier", text)
        self.assertIn("Copier le bilan", text)
        self.assertIn("Narratrice vs Athéna", text)
        self.assertIn("Ulysse vs Télémaque", text)
        self.assertIn("Français des quatre sentinelles", text)
        self.assertIn('value="PASS">PASS — autoriser P2', text)
        self.assertIn('value="FAIL">FAIL — préparer P1 ciblé v2', text)
        self.assertNotIn("download=", text.lower())
        self.assertNotIn("exporter un fichier", text.lower())

    def test_static_build_publishes_review_page_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p1.mp3", built)
        self.assertIn("Aucun fichier à exporter", built)

if __name__ == "__main__":
    unittest.main()
