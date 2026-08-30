import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-p4.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-p4.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-p4-review-v1"
CANDIDATE = "a45e8375dcc54109992dc99b767c9d5988c19b53"
AUDIO_SHA = "6ed18864c501d2450c20176f6309e7fc9c5b65485ebb33d17c69a65a7c2b445f"

class OdysseeP4ReviewSurfaceTests(unittest.TestCase):
    def test_review_page_is_bound_to_durable_release(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p4.mp3", text)
        self.assertIn(CANDIDATE, text)
        self.assertIn(AUDIO_SHA, text)
        self.assertIn("La Sirène attire-t-elle sans cliché", text)
        self.assertIn("Pouvoir d’attraction", text)
        self.assertIn("Cliché séduction / mystique", text)
        self.assertIn("La proposition vise juste pour Ulysse", text)
        self.assertIn("Copier le bilan", text)
        self.assertIn('value="PASS">PASS — autoriser P5', text)
        self.assertIn('value="FAIL">FAIL — corriger P4', text)
        self.assertNotIn("download=", text.lower())

    def test_static_build_publishes_review_page_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p4.mp3", built)
        self.assertIn("Aucun fichier à exporter", built)

if __name__ == "__main__":
    unittest.main()
