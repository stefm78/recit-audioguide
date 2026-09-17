import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "series" / "seville-discovery-v2"
SCENES = V2 / "scenes" / "FRIDAY_MORNING_SCENE_PROGRAM.json"
MANIFEST = V2 / "audio" / "FRIDAY_MORNING_AUDIO_MANIFEST.json"


class SevilleV2FridayAudioProductionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene_program = json.loads(SCENES.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.primary = cls.scene_program["scenes"]
        cls.entries = cls.manifest["entries"]

    def test_exact_primary_cardinality_and_optional_depth_boundary(self):
        self.assertEqual(8, len(self.primary))
        self.assertEqual(8, len(self.entries))
        self.assertEqual(3, len(self.scene_program["optional_depth"]))
        self.assertEqual(0, self.manifest["production_contract"]["optional_depth_audio_count"])
        self.assertEqual(
            "DEFERRED_UNTIL_COORDINATION_ACCEPTS",
            self.manifest["production_contract"]["optional_depth_disposition"],
        )
        audio_programs = sorted((V2 / "audio").glob("SEV2-FRI-AM-*.json"))
        self.assertEqual(8, len(audio_programs))
        self.assertFalse(any("-D0" in path.name for path in audio_programs))

    def test_scene_to_program_mapping_is_exact_and_deterministic(self):
        by_scene = {scene["scene_id"]: scene for scene in self.primary}
        self.assertEqual(set(by_scene), {entry["scene_id"] for entry in self.entries})
        for entry in self.entries:
            scene = by_scene[entry["scene_id"]]
            path = ROOT / entry["program_path"]
            raw = path.read_bytes()
            program = json.loads(raw.decode("utf-8"))
            self.assertEqual(scene["scene_id"], program["id"])
            self.assertEqual(scene["short_label"], program["title"])
            self.assertEqual(scene["route_section"], program["stop"])
            self.assertEqual(scene["trigger_or_launch_condition"], program["launch"])
            self.assertEqual(scene["primary_cue"], program["look"])
            self.assertEqual(1, len(program["segments"]))
            self.assertEqual(scene["spoken_text"], program["segments"][0]["text"])
            self.assertEqual(
                hashlib.sha256(scene["spoken_text"].encode("utf-8")).hexdigest(),
                entry["spoken_text_sha256"],
            )
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["program_sha256"])

    def test_french_lock_and_clean_voice_contract(self):
        self.assertEqual("PASS_BY_SOURCE_IDENTITY", self.manifest["french_lock"]["status"])
        self.assertEqual(0, self.manifest["french_lock"]["editorial_rewrite_count"])
        for entry in self.entries:
            program = json.loads((ROOT / entry["program_path"]).read_text(encoding="utf-8"))
            self.assertEqual("fr-FR", program["language"])
            self.assertEqual("speech", program["profile"])
            self.assertNotIn("soundscape", program)
            self.assertNotIn("ambience", program)
            self.assertEqual("narrateur-vif", program["segments"][0]["preset"])

    def test_engine_and_playback_contract_is_pinned(self):
        contract = self.manifest["production_contract"]
        self.assertEqual(
            "3392d4f22f0a9b054a05b5c05a7856985c0ab030",
            contract["audio_engine_pin"],
        )
        self.assertEqual("scene-level MP3", contract["playback_unit"])
        for entry in self.entries:
            self.assertEqual(
                f"generated/audio/{entry['scene_id']}/audio.mp3",
                entry["rendered_audio_path"],
            )
            self.assertEqual(
                f"generated/audio/{entry['scene_id']}/manifest.json",
                entry["rendered_manifest_path"],
            )


if __name__ == "__main__":
    unittest.main()
