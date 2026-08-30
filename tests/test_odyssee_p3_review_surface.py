import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-p3.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-p3.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-p3-review-v1"
CANDIDATE = "86b3654002073cfc4b7491265f5c3ef4ee744a3d"
AUDIO_SHA = "4f3e55c4bc22d386455cd97dd49b7a1f0363252a8b5b2a25ed718b56e8090dc0"

class OdysseeP3ReviewSurfaceTests(unittest.TestCase):
    def test_review_page_is_bound_to_durable_release(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p3.mp3", text)
        self.assertIn(CANDIDATE, text)
        self.assertIn(AUDIO_SHA, text)
        self.assertIn("Polyphème est-il grand sans qu’on triche", text)
        self.assertIn("Distinction Ulysse / Euryloque", text)
        self.assertIn("Fonctionne sec", text)
        self.assertIn("Copier le bilan", text)
        self.assertIn('value="PASS">PASS — autoriser P4', text)
        self.assertIn('value="FAIL">FAIL — corriger P3', text)
        self.assertNotIn("download=", text.lower())
        self.assertNotIn("exporter un fichier", text.lower())

    def test_static_build_publishes_review_page_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p3.mp3", built)
        self.assertIn("Aucun fichier à exporter", built)

if __name__ == "__main__":
    unittest.main()
