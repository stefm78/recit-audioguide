import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "pr42.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "pr42.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/pr42-human-review-v2"
MASTER_SHA = "4fa33d168796ef745dc9bfae95ec58135490b673c048c998c8bda029d3674893"

class PR42ReviewSurfaceTests(unittest.TestCase):
    def test_review_page_is_bound_to_durable_release(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/master.mp3", text)
        for index in range(3, 8):
            self.assertIn(f"{RELEASE}/event-{index:02d}.mp3", text)
        self.assertIn(MASTER_SHA, text)
        self.assertIn("Bilan à copier", text)
        self.assertIn("V3_TARGETED", text)
        self.assertNotIn("12:06", text)

    def test_static_build_publishes_review_page_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/master.mp3", built)
        self.assertIn("Copier le bilan", built)

if __name__ == "__main__":
    unittest.main()
