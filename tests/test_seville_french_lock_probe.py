import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "seville_french_lock_probe",
    ROOT / "tools" / "seville_french_lock_probe.py",
)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class SevilleFrenchLockProbeTests(unittest.TestCase):
    def test_inventory_is_exactly_declared_french_seville_set(self):
        inventory = probe.build_inventory(ROOT)
        self.assertEqual(inventory["program_count"], 28)
        self.assertGreater(inventory["segment_count"], 0)
        self.assertTrue(inventory["programs"])
        self.assertTrue(all(item["language"] == "fr-FR" for item in inventory["programs"]))

    def test_ab_keeps_text_identical_and_changes_only_synthesis_identity_for_lock(self):
        source = probe.load_json(
            ROOT / "series" / probe.SERIES / "audio" / "seville-discovery-ep02.json"
        )
        _, first = probe.first_segment_containing(source, "Puerta del León")
        _, second = probe.first_segment_containing(source, "Patio de las Doncellas")
        selected = [first, second]

        old = probe.minimal_program(
            source,
            program_id="old",
            title="old",
            selected=selected,
            french_lock=False,
        )
        locked = probe.minimal_program(
            source,
            program_id="locked",
            title="locked",
            selected=selected,
            french_lock=True,
        )

        self.assertTrue(probe.text_identity(old, locked))
        self.assertTrue(all(segment.get("preset") == "narrateur-vif" for segment in old["segments"]))
        for segment in locked["segments"]:
            self.assertNotIn("preset", segment)
            self.assertEqual(segment["voice"], probe.LOCK_VOICE)
            self.assertEqual(segment["rate"], probe.RATE)
            self.assertEqual(segment["pitch"], probe.PITCH)
            self.assertEqual(segment["volume"], probe.VOLUME)

    def test_lock_voice_is_native_french_not_multilingual(self):
        self.assertTrue(probe.LOCK_VOICE.startswith("fr-FR-"))
        self.assertNotIn("Multilingual", probe.LOCK_VOICE)
        self.assertIn("Multilingual", probe.BASELINE_VOICE)

    def test_control_selection_is_long_and_low_spanish_proper_surface_pressure(self):
        source = probe.load_json(
            ROOT / "series" / probe.SERIES / "audio" / "seville-discovery-g03.json"
        )
        _, segment = probe.choose_control_segment(source)
        self.assertGreaterEqual(len(segment["text"]), 180)
        hits = probe.proper_surface_hits(segment["text"])
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
