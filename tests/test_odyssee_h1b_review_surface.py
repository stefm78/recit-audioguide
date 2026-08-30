import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "reviews" / "odyssee-h1b.html"
DIST_PAGE = ROOT / "dist" / "reviews" / "odyssee-h1b.html"
RELEASE = "https://github.com/stefm78/recit-audioguide/releases/download/odyssee-h1b-corrective-review-v1"
SOURCE = "feb27315dd159a0ab1c071eee39eb106edebcea7"
DIGESTS = {
    "p4-a":"6801dbc716226d60af1a7aade963a636bdd65089897d2ff381295e1747c48e58",
    "p4-b":"14f325e3a1404c260c9a5139b85bcb5267cdd91a60c2458ea80bd66f3d75365d",
    "p5-a":"4bbefbf7391cdaa1fd995169e9e971b00b649afc4071354dc9302cd960c34895",
    "p5-b":"1372fafc5f47a26aa9e25320c822f6df129a4f08abe296b1bedc45bf24d55a22",
    "p6-a":"585ff7d54b409524670d16aa67f418ec61928f333b4911191850ffb44a249565",
    "p6-b":"474c2e41a5d702b2a84524aa3be9a0559ed7378af18d507ac082b666029d64ae",
}

class OdysseeH1BReviewSurfaceTests(unittest.TestCase):
    def test_page_binds_all_six_immutable_candidates(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn(SOURCE, text)
        for name,digest in DIGESTS.items():
            self.assertIn(f"{RELEASE}/{name}.mp3", text)
            self.assertIn(digest, text)

    def test_atomic_verdicts_and_corrective_questions(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("DÉCISION P4", text)
        self.assertIn("DÉCISION P5", text)
        self.assertIn("DÉCISION P6", text)
        self.assertIn("mots ou prononciations anglaises", text)
        self.assertNotIn("Ulysse est-il suffisamment conteur ici", text)
        self.assertIn("Copier le bilan", text)
        self.assertIn("Aucun fichier à exporter", text)
        self.assertNotIn("download=", text.lower())

    def test_static_build_publishes_h1b_without_audio_generation(self):
        subprocess.run([sys.executable, "site/build.py"], cwd=ROOT, check=True)
        self.assertTrue(DIST_PAGE.is_file())
        built = DIST_PAGE.read_text(encoding="utf-8")
        self.assertIn(f"{RELEASE}/p4-a.mp3", built)
        self.assertIn(f"{RELEASE}/p6-b.mp3", built)

if __name__ == "__main__":
    unittest.main()
