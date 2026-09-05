from html.parser import HTMLParser
from pathlib import Path
import unittest

PAGE = Path("web/reviews/odyssee-p6-s15-capture-v2.html")
EXPECTED = [112, 114, 116, 118, 120, 133, 135, 140, 142, 151, 153, 158]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slots = []
        self.record = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("data-seg"):
            self.slots.append(int(a["data-seg"]))
        if tag == "button" and a.get("data-record"):
            self.record.append(int(a["data-record"]))

class CaptureV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.p = Parser(); cls.p.feed(cls.html)

    def test_12_static_capture_slots_exist_without_js_render_dependency(self):
        self.assertEqual(self.p.slots, EXPECTED)
        self.assertEqual(self.p.record, EXPECTED)
        self.assertNotIn('id="cards"', self.html)
        self.assertNotIn("renderCards", self.html)

    def test_same_origin_recovery_uses_historical_indexeddb_namespace(self):
        self.assertIn("odyssee-p6-s15-production-recordings-v1", self.html)
        self.assertIn("https://stefm78.github.io", self.html)
        self.assertIn("same-origin historique", self.html)

    def test_runtime_capabilities_are_visible(self):
        for token in ("JavaScript :", "Micro/MediaRecorder :", "IndexedDB :", "SHA-256 :"):
            self.assertIn(token, self.html)
        self.assertIn("navigator.mediaDevices.getUserMedia", self.html)
        self.assertIn("MediaRecorder", self.html)
        self.assertIn("crypto.subtle.digest", self.html)

    def test_duration_bounds_match_private_intake(self):
        self.assertIn("MIN=.20,MAX=20", self.html)
        self.assertIn("0,20 s et 20,0 s", self.html)
        self.assertIn("x.duration<MIN||x.duration>MAX", self.html)

    def test_export_contract_is_canonical_and_private(self):
        for token in (
            "odyssee-p6-s15-production-human-capture-v1",
            "FROZEN_SELECTED_TAKES_READY_FOR_SINGLE_BELTOUT_CONVERSION",
            "EXACTLY_ONE_BELTOUT_CONVERSION_PER_SELECTED_TAKE",
            "constant_level_alignment_only",
            "NEVER_COMMIT_TO_PUBLIC_REPOSITORY",
            "recording-manifest.json",
            "SHA256SUMS.txt",
            "odyssee-p6-s15-production-selected-takes.zip",
        ):
            self.assertIn(token, self.html)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

if __name__ == "__main__":
    unittest.main()
