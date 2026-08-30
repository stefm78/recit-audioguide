import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_odyssee_script", ROOT / "tools" / "validate_odyssee_script.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OdysseeScriptTest(unittest.TestCase):
    def test_full_script_contract(self):
        report = MODULE.validate()
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["total_spoken_words"], 11788)
        sequences = []
        for block in report["blocks"].values():
            sequences.extend(block["sequences"])
        self.assertEqual(sorted(sequences), list(range(1, 16)))


if __name__ == "__main__":
    unittest.main()
