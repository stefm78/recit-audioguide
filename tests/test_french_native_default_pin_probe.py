import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "french_native_default_pin_probe",
    ROOT / "tools" / "french_native_default_pin_probe.py",
)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class FrenchNativeDefaultPinProbeTests(unittest.TestCase):
    def test_engine_refs_and_voice_contract_are_frozen(self):
        self.assertEqual(probe.OLD_ENGINE_REF, "3392d4f22f0a9b054a05b5c05a7856985c0ab030")
        self.assertEqual(probe.NEW_ENGINE_REF, "2fc024ee41984e2d9eaa454cf4edeeb3e63c741c")
        self.assertEqual(probe.OLD_VOICE, "fr-FR-RemyMultilingualNeural")
        self.assertEqual(probe.NEW_VOICE, "fr-FR-HenriNeural")
        self.assertNotIn("Multilingual", probe.NEW_VOICE)

    def test_representative_cases_are_fr_fr_narrateur_vif(self):
        for case_name, case in probe.CASE_DEFS.items():
            data = json.loads((ROOT / case["path"]).read_text(encoding="utf-8"))
            self.assertEqual(data.get("language"), "fr-FR", case_name)
            _, segments = probe.select_segments(data, case["selectors"])
            self.assertTrue(segments, case_name)
            self.assertTrue(all(seg.get("preset") == "narrateur-vif" for seg in segments), case_name)

    def test_odyssee_control_is_explicit_cast(self):
        data = json.loads((ROOT / probe.ODYSSEE_CONTROL).read_text(encoding="utf-8"))
        sampled = data.get("segments", [])[:5]
        self.assertTrue(sampled)
        self.assertTrue(all(seg.get("voice") for seg in sampled))
        self.assertTrue(any("Multilingual" in seg["voice"] for seg in sampled))

    def test_workflow_has_no_publish_or_field_action(self):
        workflow = (ROOT / ".github" / "workflows" / "french-native-default-pin-candidate.yml").read_text(encoding="utf-8")
        forbidden = ["deploy-pages", "android-field-latest", "upload-pages-artifact", "workflow_dispatch"]
        for marker in forbidden:
            self.assertNotIn(marker, workflow)
        self.assertIn("audit/french-native-default-pin-20260913", workflow)


if __name__ == "__main__":
    unittest.main()
