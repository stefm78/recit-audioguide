import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-p2.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-p2.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-p2-review-v1"
CANDIDATE = "67a22afc7d3f61a67f04706beeb313ffe5fefc54"
AUDIO_SHA = "31b8055dde3b5521952559ec49a988fe8c055bdd2e738f6b0e03671ad91df4e9"

class OdysseeP2ReviewSurfaceTests(unittest.TestCase):
    def test_review_page_is_bound_to_durable_release(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p2.mp3", text)
        self.assertIn(CANDIDATE, text)
        self.assertIn(AUDIO_SHA, text)
        self.assertIn("Bilan à copier", text)
        self.assertIn("Copier le bilan", text)
        self.assertIn("Clarté de la bascule narratrice", text)
        self.assertIn("Après « Nous avions quitté Troie… », qui porte le récit ?", text)
        self.assertIn("Identité d’Ulysse vs P1", text)
        self.assertIn('value="PASS">PASS — autoriser P3', text)
        self.assertIn('value="FAIL">FAIL — préparer P2 ciblé v2', text)
        self.assertNotIn("download=", text.lower())
        self.assertNotIn("exporter un fichier", text.lower())

    def test_static_build_publishes_review_page_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p2.mp3", built)
        self.assertIn("Aucun fichier à exporter", built)

if __name__ == "__main__":
    unittest.main()
