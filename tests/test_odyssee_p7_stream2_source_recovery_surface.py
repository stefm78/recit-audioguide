from pathlib import Path
import unittest

PAGE = Path("web/reviews/odyssee-p7-stream2-source-recovery.html")

EXPECTED = {
    "S05-135": "a7acb1ce12d85d64e373689a7799dd747b583b2c55f98ec5fecc652db41b6392",
    "S05-139": "fbf36362726ef1788b8503bc223aeb2683f8a681cae4a9bddb571ff1a3eea43f",
    "S05-143": "50b6e7f2ec9906f0b4de21ce98b52830f2266e7efe95f70cfa525d895121777e",
    "S06-090": "725f80ffe6632baf6ccf5ea8ca723f9530d1b356983cf67a73b1a4e7bfdff577",
    "S06-093": "49d60bdbccc509980f50d68e02b78944c9f8894d893a2fd648f41aba7b6a427d",
    "S06-099": "0083e7c3418d6171043a14bcbb6d39dde6dd0950c316bd45f4ba338346919851",
    "S14-079": "9f2a9239ad952a8d255006933603216829ba878d683c8ac9f53bb9652bbbdef4",
    "S14-085": "2188b5403c0a35998c0b43e378856de500797fbf67daf18278a7f611545ac834",
    "S14-089": "0b9cb6f0da04deef1d0166c418d2f7d67c748698aa124b5d3a675f3816c28d6d",
}


class TestP7Stream2SourceRecoverySurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_targets_exact_historical_p7_database(self):
        self.assertIn("odyssee-p7-stream2-human-beltout-v1", self.html)
        self.assertIn("const STORE='takes'", self.html)
        self.assertNotIn("odyssee-p6-s15-production-recordings-v1", self.html)

    def test_all_nine_frozen_source_hashes_are_bound(self):
        for target, digest in EXPECTED.items():
            self.assertIn(target, self.html)
            self.assertIn(digest, self.html)
        self.assertEqual(self.html.count("file:'S"), 9)

    def test_recovery_is_local_read_only(self):
        self.assertIn("crypto.subtle.digest('SHA-256'", self.html)
        self.assertIn("transaction(STORE,'readonly')", self.html)
        self.assertNotIn("'readwrite'", self.html)
        self.assertNotIn(".put(", self.html)
        self.assertNotIn("createObjectStore", self.html)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)
        self.assertIn("r.transaction.abort()", self.html)

    def test_export_is_fail_closed_on_exact_nine(self):
        self.assertIn("keys.some(k=>!recovered[k])", self.html)
        self.assertIn("n!==keys.length", self.html)
        self.assertIn("odyssee-p7-stream2-human-beltout-source-recovered-exact.zip", self.html)
        self.assertIn("9/9 blobs exacts", self.html)


if __name__ == "__main__":
    unittest.main()
