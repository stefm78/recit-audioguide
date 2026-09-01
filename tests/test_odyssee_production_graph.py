import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ODYSSEE = ROOT / "series" / "odyssee"
PROGRAMS = ODYSSEE / "programs"
PRODUCTION = ODYSSEE / "production"
MANIFEST_PATH = PRODUCTION / "ODYSSEE_PRODUCTION_MANIFEST_V1.json"
VOICE_PACK_PATH = PRODUCTION / "voice-packs" / "ODYSSEE_PRODUCTION_V1.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def parse_source(path):
    result = {}
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        header = re.match(r"^# (S\d{2}) — (.+)$", raw)
        if header:
            current = header.group(1)
            result[current] = []
            continue
        line = re.match(r"^(.+?) — (.+)$", raw)
        if current and line:
            result[current].append((line.group(1).strip(), line.group(2).strip()))
    return result


class OdysseeProductionGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.voice_pack = json.loads(VOICE_PACK_PATH.read_text(encoding="utf-8"))
        cls.presets = {item["id"]: item for item in cls.voice_pack["presets"]}
        cls.units = {item["id"]: item for item in cls.manifest["units"]}

    def test_all_frozen_spoken_lines_are_copied_exactly_once_into_scene_programs(self):
        all_source = {}
        for block in ("a", "b", "c", "d"):
            all_source.update(parse_source(ODYSSEE / "text" / f"block-{block}.md"))

        self.assertEqual(sorted(all_source), [f"S{i:02d}" for i in range(1, 16)])
        for scene_id, expected in all_source.items():
            program = json.loads((PROGRAMS / f"{scene_id}.json").read_text(encoding="utf-8"))
            actual = [(item["speaker"], item["text"]) for item in program["segments"]]
            self.assertEqual(actual, expected, scene_id)

    def test_stream1_source_blob_bindings_are_still_exact(self):
        handoff = json.loads((PRODUCTION / "STREAM3_HANDOFF_V1.json").read_text(encoding="utf-8"))
        for block in handoff["blocks"]:
            path = ROOT / block["source"]
            self.assertEqual(git_blob_sha1(path), block["source_blob"], block["id"])

    def test_manifest_hashes_pin_every_program_and_voice_pack(self):
        expected_voice_sha = sha256(VOICE_PACK_PATH)
        for scene_id in [f"S{i:02d}" for i in range(1, 16)]:
            unit = self.units[scene_id]
            self.assertEqual(unit["program_sha256"], sha256(ROOT / unit["program"]), scene_id)
            self.assertEqual(unit["voice_pack_sha256"], expected_voice_sha, scene_id)
            self.assertEqual(ROOT / unit["voice_pack"], VOICE_PACK_PATH)

    def test_only_true_external_or_provider_gaps_are_held(self):
        held = {uid for uid, unit in self.units.items() if unit["state"] == "hold"}
        self.assertEqual(held, {"S08", "S09", "S15"})
        for scene_id in set(self.units) - held:
            self.assertEqual(self.units[scene_id]["provider"], "edge")
            program = json.loads((PROGRAMS / f"{scene_id}.json").read_text(encoding="utf-8"))
            for segment in program["segments"]:
                preset = self.presets[segment["preset"]]
                self.assertEqual(preset["provider"], "edge", f"{scene_id}: {segment['preset']}")
                self.assertFalse(str(preset["voice"]).startswith("provider-slot:"), scene_id)

    def test_block_graph_is_exact_and_master_stays_held_while_required_scenes_are_held(self):
        assemblies = {item["id"]: item["units"] for item in self.manifest["assemblies"]}
        self.assertEqual(assemblies, {
            "A": ["S01", "S02", "S03", "S04"],
            "B": ["S05", "S06", "S07", "S08"],
            "C": ["S09", "S10", "S11"],
            "D": ["S12", "S13", "S14", "S15"],
        })
        self.assertEqual(self.manifest["master"]["assemblies"], ["A", "B", "C", "D"])
        self.assertTrue(any(self.units[scene]["state"] == "hold" for scene in assemblies["B"]))
        self.assertTrue(any(self.units[scene]["state"] == "hold" for scene in assemblies["C"]))
        self.assertTrue(any(self.units[scene]["state"] == "hold" for scene in assemblies["D"]))

    def test_s15_does_not_guess_p6_probe_to_frozen_scene_mapping(self):
        program = json.loads((PROGRAMS / "S15.json").read_text(encoding="utf-8"))
        self.assertIn("P6_FROZEN_S15_LINE_BINDING", program["production"]["blockers"])
        self.assertFalse(any("external_voice_slot" in segment for segment in program["segments"]))


if __name__ == "__main__":
    unittest.main()
