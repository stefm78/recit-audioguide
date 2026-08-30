import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
EXPECTED_PIN = "3392d4f22f0a9b054a05b5c05a7856985c0ab030"


def extract_audio_engine_pins(text):
    pins = []

    for match in re.finditer(
        r"uses:\s*stefm78/audio-engine/[^\s]+@([0-9a-f]{40})",
        text,
    ):
        pins.append(("reusable-workflow", match.group(1)))

    for match in re.finditer(
        r"engine_ref:\s*[\"']?([0-9a-f]{40})",
        text,
    ):
        pins.append(("engine-ref", match.group(1)))

    for match in re.finditer(
        r"repository:\s*stefm78/audio-engine\s*\n\s*ref:\s*([0-9a-f]{40})",
        text,
    ):
        pins.append(("checkout", match.group(1)))

    return pins


class AudioEnginePinCoherenceTests(unittest.TestCase):
    def test_all_consumer_runtime_pins_are_identical_and_proven(self):
        pins = extract_audio_engine_pins(WORKFLOW.read_text(encoding="utf-8"))
        self.assertEqual(len(pins), 4, pins)
        self.assertEqual({sha for _, sha in pins}, {EXPECTED_PIN}, pins)

    def test_expected_pin_is_immutable_in_this_work_package(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(EXPECTED_PIN, text)
        self.assertNotIn(
            "294a1d84687199007dd7d542466ff39b2b4ac353",
            text,
            "current audio-engine main must not be promoted implicitly",
        )


if __name__ == "__main__":
    unittest.main()
