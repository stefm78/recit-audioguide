import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence" / "nuit-apres-orleans-production-plan-fit-2026-08-30.json"


def contains_key(value, wanted):
    if isinstance(value, dict):
        return wanted in value or any(contains_key(v, wanted) for v in value.values())
    if isinstance(value, list):
        return any(contains_key(v, wanted) for v in value)
    return False


class LongformProductionPlanAuditTests(unittest.TestCase):
    def setUp(self):
        self.audit = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_exact_read_only_source_authority(self):
        source = self.audit["source"]
        self.assertEqual(source["pull_request"], 42)
        self.assertEqual(source["head"], "203268827d5c5e7d7312545f465b653c5bd31690")
        self.assertEqual(source["program"]["git_blob_sha1"], "a966f1e6572d8ed7897181ce7c404d3cf10d6a34")
        self.assertEqual(source["sound_direction"]["git_blob_sha1"], "a51f7799bd5be6ac44913aa19ab0b1dae5f7470d")
        self.assertEqual(source["series"]["git_blob_sha1"], "6dff9bfe13ca77adc3370ba42aed73591d0bcecf")

    def test_observed_shape_is_internally_consistent(self):
        observed = self.audit["observed"]
        self.assertEqual(observed["segments"], 150)
        self.assertEqual(len(observed["scenes"]), 9)
        self.assertEqual(sum(v["segments"] for v in observed["roles"].values()), 150)
        self.assertEqual(observed["sound_direction_beats"], 13)
        self.assertEqual(observed["sound_events"], 7)
        cursor = 1
        for scene in observed["scenes"]:
            start, end = scene["segment_range"]
            self.assertEqual(start, cursor)
            self.assertGreaterEqual(end, start)
            cursor = end + 1
        self.assertEqual(cursor, 151)

    def test_program_ref_avoids_second_text_authority(self):
        plan = self.audit["proposed_production_plan"]
        self.assertEqual(plan["content_binding"]["mode"], "program-ref")
        self.assertEqual(plan["content_binding"]["content_authority"], "program")
        self.assertFalse(contains_key(plan, "text"))
        self.assertEqual(plan["content_binding"]["git_blob_sha1"], self.audit["source"]["program"]["git_blob_sha1"])
        self.assertEqual(len(plan["overlays"]), 9)

    def test_acting_variation_requires_preservation_not_normalization(self):
        roles = self.audit["observed"]["roles"]
        self.assertGreaterEqual(roles["martin"]["voice_variants"], 20)
        self.assertGreaterEqual(roles["agnes"]["voice_variants"], 10)
        self.assertEqual(self.audit["decision"]["binding_mode"], "program-ref")

    def test_legacy_strategy_is_explicitly_lossy(self):
        legacy = self.audit["legacy_scene_sequences"]
        self.assertFalse(legacy["applicable"])
        self.assertEqual(legacy["hardcoded_bridge_defaults"]["foreground_ms"], 3200)
        self.assertEqual(legacy["hardcoded_bridge_defaults"]["carry_under_speech_ms"], 7000)
        authored = legacy["authored_bridge_examples"]
        self.assertEqual([x["foreground_ms"] for x in authored], [1000, 2300, 4200, 3000])
        self.assertEqual(self.audit["decision"]["legacy_scene_sequences"], "DO_NOT_APPLY")

    def test_human_gate_is_not_bypassed(self):
        self.assertEqual(
            self.audit["decision"]["human_gate"],
            "UNCHANGED_PR_42_LISTENING_REQUIRED_BEFORE_PRODUCT_PROMOTION",
        )


if __name__ == "__main__":
    unittest.main()
