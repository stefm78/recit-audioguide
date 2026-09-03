from pathlib import Path
import unittest

PAGE=Path("web/reviews/odyssee-p7-stream2-human-beltout.html")
CONTRACT=Path("series/odyssee/review/P7_STREAM2_HUMAN_BELTOUT_GENERALIZATION_V1.json")

class TestP7Stream2HumanBeltoutSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=PAGE.read_text(encoding="utf-8")
        cls.contract=CONTRACT.read_text(encoding="utf-8")

    def test_exact_nine_frozen_lines(self):
        pairs={
            135:"Je lui ai dit que ce n’était pas Personne. Que c’était Ulysse, roi d’Ithaque, qui lui avait pris son œil.",
            139:"Pour que quelqu’un sache.",
            143:"Après mon cri, elle est devenue personnelle.",
            90:"Je me suis réveillé quand le bateau a changé sous mon corps.",
            93:"Ithaque s’éloignait.",
            99:"Nous avions notre île devant nous.",
            79:"Pose ce que tu tiens.",
            85:"Tu vas rendre les années à Pénélope ?",
            89:"Alors cesse de proposer des comptes que tu sais faux.",
        }
        for segment,text in pairs.items():
            self.assertIn(str(segment),self.html)
            self.assertIn(text,self.html)
            self.assertIn(text,self.contract)

    def test_exact_c2_comparators(self):
        self.assertIn("odyssee-p7-round2-line-microprosody-v1",self.html)
        for name,sha in (
            ("p7-r2-storyteller-c.mp3","bf3708c59d29265454be527b99d1e7a00d68c0b494de34c1de7f0e19b4e15943"),
            ("p7-r2-loss-c.mp3","4d3f737caa745db4339b12c40c780048579fb31cfa5f18d6d9f47aa988f09049"),
            ("p7-r2-authority-c.mp3","59930ee6802957e78b345131092a03b5e1bc4d79c3dc56c44f25e433b602003b"),
        ):
            self.assertIn(name,self.html)
            self.assertIn(sha,self.html)

    def test_local_first_private_recording(self):
        self.assertIn("navigator.mediaDevices.getUserMedia",self.html)
        self.assertIn("MediaRecorder",self.html)
        self.assertIn("indexedDB.open",self.html)
        self.assertIn("aucun upload automatique",self.html.lower())
        self.assertNotIn("fetch(",self.html)
        self.assertNotIn("XMLHttpRequest",self.html)
        self.assertIn("raw_human_audio_public_repo_forbidden",self.contract)

    def test_freeze_and_integrity_export(self):
        self.assertIn('crypto.subtle.digest("SHA-256"',self.html)
        self.assertIn("odyssee-p7-stream2-human-beltout-source.zip",self.html)
        self.assertIn("recording-manifest.json",self.html)
        self.assertIn("selection_before_beltout",self.html)

    def test_constraints_are_explicit(self):
        for phrase in (
            "Aucun best-of-N",
            "No Round 3 Edge",
            "materially_more_alive_and_less_mechanical_cold_than_C2",
            "dramatization_appropriate_and_restrained",
        ):
            self.assertTrue(phrase in self.contract or phrase in self.html)

if __name__=="__main__":
    unittest.main()
