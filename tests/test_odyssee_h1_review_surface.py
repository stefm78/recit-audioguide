import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-h1.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-h1.html"

P4_RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-h1-p4-chatterbox-review-v2"
P56_RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-h1-p5p6-review-v1"
P4A = "bcb3af5b0d350db12128d891ab8211c73cf0a608eba68af7c7bb7cf1db4cfacd"
P4B = "3c759eda2c7a683ec550fc9ed35adca3eb9bc88ac740af93868158b4cb9746a3"
P5 = "e102218a90f76783959f7f2f7b165babeecbc7411994b3b2c2568df9ca77efc5"
P6 = "53d389e45dcc3120a652d7c4bbb030e1fdedf7f78d0041edeb17f5469f349897"

class OdysseeH1ReviewSurfaceTests(unittest.TestCase):
    def test_page_binds_every_immutable_candidate(self):
        text = PAGE.read_text(encoding="utf-8")
        for url in (
            f"{P4_RELEASE}/p4-a.mp3",
            f"{P4_RELEASE}/p4-b.mp3",
            f"{P56_RELEASE}/p5.mp3",
            f"{P56_RELEASE}/p6.mp3",
        ):
            self.assertIn(url, text)
        for digest in (P4A, P4B, P5, P6):
            self.assertIn(digest, text)

    def test_batch_keeps_atomic_verdicts_and_cross_checks(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("DÉCISION P4", text)
        self.assertIn("DÉCISION P5", text)
        self.assertIn("DÉCISION P6", text)
        self.assertIn("Ulysse est-il suffisamment conteur ici", text)
        self.assertIn("Anticlée et Pénélope", text)
        self.assertIn("Identité d’Ulysse stable", text)
        self.assertIn("Copier le bilan", text)
        self.assertIn("Aucun fichier à exporter", text)
        self.assertNotIn("download=", text.lower())

    def test_static_build_publishes_h1_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{P4_RELEASE}/p4-a.mp3", built)
        self.assertIn(f"{P56_RELEASE}/p6.mp3", built)

if __name__ == "__main__":
    unittest.main()
