from pathlib import Path
import unittest

PAGE=Path("web/reviews/odyssee-p7-stream2-human-beltout.html")
RECOVERY_PAGE=Path("web/reviews/odyssee-p7-stream2-source-recovery.html")
CONTRACT=Path("series/odyssee/review/P7_STREAM2_HUMAN_BELTOUT_GENERALIZATION_V1.json")

RECOVERY_SHA={
    "S05-135":"a7acb1ce12d85d64e373689a7799dd747b583b2c55f98ec5fecc652db41b6392",
    "S05-139":"fbf36362726ef1788b8503bc223aeb2683f8a681cae4a9bddb571ff1a3eea43f",
    "S05-143":"50b6e7f2ec9906f0b4de21ce98b52830f2266e7efe95f70cfa525d895121777e",
    "S06-090":"725f80ffe6632baf6ccf5ea8ca723f9530d1b356983cf67a73b1a4e7bfdff577",
    "S06-093":"49d60bdbccc509980f50d68e02b78944c9f8894d893a2fd648f41aba7b6a427d",
    "S06-099":"0083e7c3418d6171043a14bcbb6d39dde6dd0950c316bd45f4ba338346919851",
    "S14-079":"9f2a9239ad952a8d255006933603216829ba878d683c8ac9f53bb9652bbbdef4",
    "S14-085":"2188b5403c0a35998c0b43e378856de500797fbf67daf18278a7f611545ac834",
    "S14-089":"0b9cb6f0da04deef1d0166c418d2f7d67c748698aa124b5d3a675f3816c28d6d",
}

class TestP7Stream2HumanBeltoutSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=PAGE.read_text(encoding="utf-8")
        cls.recovery=RECOVERY_PAGE.read_text(encoding="utf-8")
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
            "best_of_N",
            "round3_edge",
            "materially_more_alive_and_less_mechanical_cold_than_C2",
            "dramatization_appropriate_and_restrained",
        ):
            self.assertTrue(phrase in self.contract or phrase in self.html)

    def test_recovery_targets_exact_p7_database_not_p6_database(self):
        self.assertIn("odyssee-p7-stream2-human-beltout-v1",self.recovery)
        self.assertIn("const STORE='takes'",self.recovery)
        self.assertNotIn("odyssee-p6-s15-production-recordings-v1",self.recovery)

    def test_recovery_binds_all_nine_frozen_source_sha(self):
        for target,digest in RECOVERY_SHA.items():
            self.assertIn(target,self.recovery)
            self.assertIn(digest,self.recovery)
        self.assertEqual(self.recovery.count("file:'S"),9)

    def test_recovery_is_local_read_only_and_fail_closed(self):
        self.assertIn("crypto.subtle.digest('SHA-256'",self.recovery)
        self.assertIn("transaction(STORE,'readonly')",self.recovery)
        self.assertNotIn("'readwrite'",self.recovery)
        self.assertNotIn(".put(",self.recovery)
        self.assertNotIn("createObjectStore",self.recovery)
        self.assertNotIn("fetch(",self.recovery)
        self.assertNotIn("XMLHttpRequest",self.recovery)
        self.assertIn("r.transaction.abort()",self.recovery)
        self.assertIn("keys.some(k=>!recovered[k])",self.recovery)
        self.assertIn("n!==keys.length",self.recovery)
        self.assertIn("odyssee-p7-stream2-human-beltout-source-recovered-exact.zip",self.recovery)

if __name__=="__main__":
    unittest.main()
