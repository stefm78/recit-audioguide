import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-p4v3.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-p4v3.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-p4v3-dialogue-review-v1"
CANDIDATE = "a18706ba560e9bda21dcaf3754d32dcc702cfae8"
AUDIO_SHA = "fe1b5d7f3d129f7869a7a4335704d729f1b4b83805a67bbee0f23b23c14a592d"

class OdysseeP4V3ReviewSurfaceTests(unittest.TestCase):
    def test_review_page_is_bound_to_immutable_release(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p4v3.mp3", text)
        self.assertIn(CANDIDATE, text)
        self.assertIn(AUDIO_SHA, text)
        self.assertIn("Enfin un dialogue, ou toujours une narratrice", text)
        self.assertIn("PASS EDGE", text)
        self.assertIn("FAIL EDGE", text)
        self.assertIn("Copier le bilan", text)
        self.assertNotIn("download=", text.lower())

    def test_static_build_publishes_review_page_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p4v3.mp3", built)
        self.assertIn("Aucun fichier à exporter", built)

if __name__ == "__main__":
    unittest.main()
