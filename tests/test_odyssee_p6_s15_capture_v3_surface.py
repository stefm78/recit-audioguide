from pathlib import Path
import unittest

PAGE = Path('web/reviews/odyssee-p6-s15-capture-v3.html')
EXPECTED = [112,114,116,118,120,133,135,140,142,151,153,158]

class P6S15CaptureV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding='utf-8')

    def test_static_12_capture_slots_and_buttons(self):
        self.assertEqual(self.html.count('class="slot" data-seg='), 12)
        for seg in EXPECTED:
            self.assertIn(f'data-seg="{seg}"', self.html)
            self.assertIn(f'data-record="{seg}"', self.html)

    def test_same_origin_private_storage_contract(self):
        self.assertIn('odyssee-p6-s15-production-recordings-v1', self.html)
        self.assertIn('https://stefm78.github.io', self.html)
        self.assertNotIn('fetch(', self.html)
        self.assertNotIn('XMLHttpRequest', self.html)

    def test_live_meter_and_local_scan_exist(self):
        for token in ('meter-fill','meter-text','AudioContext','createAnalyser','scan(blob)','crête','RMS','écrêtage probable','data-wave'):
            self.assertIn(token, self.html)

    def test_export_contract_stays_canonical(self):
        for token in ('odyssee-p6-s15-production-human-capture-v1','FROZEN_SELECTED_TAKES_READY_FOR_SINGLE_BELTOUT_CONVERSION','EXACTLY_ONE_BELTOUT_CONVERSION_PER_SELECTED_TAKE','constant_level_alignment_only','NEVER_COMMIT_TO_PUBLIC_REPOSITORY','recording-manifest.json','SHA256SUMS.txt','odyssee-p6-s15-production-selected-takes.zip'):
            self.assertIn(token, self.html)
        self.assertIn("MIN=.20,MAX=20", self.html)

if __name__ == '__main__':
    unittest.main()
