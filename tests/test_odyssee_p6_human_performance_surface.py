from pathlib import Path
import unittest

PAGE = Path("web/reviews/odyssee-p6-human-performance.html")


class TestOdysseeP6HumanPerformanceSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_exact_five_target_lines_are_present(self):
        for text in (
            "Non.",
            "Ce lit ne sort pas de cette chambre.",
            "Tu le savais.",
            "Pénélope…",
            "Notre lit.",
        ):
            self.assertIn(text, self.html)

    def test_penelope_context_is_present(self):
        for text in (
            "Euryclée. Prépare le lit d’Ulysse dans le couloir.",
            "Non ?",
            "Pourquoi ?",
            "Alors personne ne l’a déplacé.",
            "Je devais savoir si toi, tu le savais encore.",
            "Ulysse.",
            "Je n’avais besoin que d’une chose qui ne puisse pas voyager avec tes histoires.",
        ):
            self.assertIn(text, self.html)

    def test_reference_audio_is_immutable_h1b_b(self):
        self.assertIn(
            "odyssee-h1b-corrective-review-v1/p6-b.mp3",
            self.html,
        )
        self.assertIn(
            "474c2e41a5d702b2a84524aa3be9a0559ed7378af18d507ac082b666029d64ae",
            self.html,
        )

    def test_browser_recording_is_local_first(self):
        self.assertIn("navigator.mediaDevices.getUserMedia", self.html)
        self.assertIn("MediaRecorder", self.html)
        self.assertIn("indexedDB.open", self.html)
        self.assertIn("aucun upload automatique", self.html.lower())
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_freeze_export_has_integrity_and_zip(self):
        self.assertIn('crypto.subtle.digest("SHA-256"', self.html)
        self.assertIn("odyssee-p6-human-performance-selected.zip", self.html)
        self.assertIn("recording-manifest.json", self.html)
        self.assertIn("One human-selected take per slot", self.html)

    def test_all_five_cue_ranges_are_frozen(self):
        for marker in (
            'cue:[0,6.736]',
            'cue:[5.976,10.734]',
            'cue:[22.272,29.208]',
            'cue:[26.648,32.924]',
            'cue:[33.404,40.12]',
        ):
            self.assertIn(marker, self.html)


if __name__ == "__main__":
    unittest.main()
