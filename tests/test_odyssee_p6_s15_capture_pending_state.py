import json
from pathlib import Path
import unittest

MANIFEST = Path("series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json")
PROGRAM = Path("series/odyssee/programs/S15.json")
BINDING = Path("series/odyssee/production/P6_FROZEN_S15_BINDING_V1.json")
READINESS = Path("series/odyssee/production/P6_STREAM3_READINESS_V1.json")
SIDECAR = Path("series/odyssee/production/H2_STREAM3_MATERIALIZATION_V1.json")
CAPTURE = Path("series/odyssee/production/P6_S15_PRODUCTION_CAPTURE_V1.json")

EXPECTED_SEGMENTS = [112, 114, 116, 118, 120, 133, 135, 140, 142, 151, 153, 158]
STATE = "P6_S15_PRODUCTION_HUMAN_CAPTURE_PENDING"


class TestP6S15CapturePendingState(unittest.TestCase):
    def load(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_manifest_keeps_s15_hold_only_on_production_capture(self):
        manifest = self.load(MANIFEST)
        s15 = next(unit for unit in manifest["units"] if unit["id"] == "S15")
        self.assertEqual(s15["state"], "hold")
        self.assertIn(STATE, s15["hold_reason"])
        self.assertNotIn("provider package is pending", s15["hold_reason"])

    def test_program_hold_matches_capture_state_without_text_rewrite(self):
        program = self.load(PROGRAM)
        self.assertEqual(program["production"]["state"], "HOLD")
        self.assertEqual(program["production"]["blockers"], [STATE])
        p6 = program["production"]["p6_ulysse"]
        self.assertEqual(p6["state"], STATE)
        self.assertEqual(p6["mapped_segments"], EXPECTED_SEGMENTS)
        self.assertEqual(p6["casting_state"], "CLOSED")
        self.assertEqual(
            p6["provider_package"],
            "series/odyssee/production/provider-packages/P6_ULYSSES_HUMAN_BELTOUT_PRODUCTION_V1.json",
        )

    def test_binding_and_readiness_exit_stream2_critical_path(self):
        binding = self.load(BINDING)["ulysses_emotional_performance"]
        readiness = self.load(READINESS)
        self.assertEqual(binding["state"], STATE)
        self.assertEqual(binding["casting_state"], "CLOSED")
        self.assertEqual(binding["stream2_state"], "EXIT_CRITICAL_PATH")
        self.assertEqual(readiness["status"], STATE)
        self.assertEqual(readiness["ulysses_emotional"]["state"], STATE)
        self.assertEqual(readiness["capture_required"], "P6_S15_PRODUCTION_HUMAN_CAPTURE_REQUIRED")

    def test_capture_contract_is_exact_and_post_conversion_is_single_pass(self):
        capture = self.load(CAPTURE)
        self.assertEqual(capture["status"], STATE)
        self.assertEqual(capture["scope"]["exact_segments"], EXPECTED_SEGMENTS)
        self.assertEqual(capture["scope"]["exact_guard_count"], 12)
        self.assertEqual(
            capture["capture"]["post_selection_conversion_rule"],
            "EXACTLY_ONE_BELTOUT_CONVERSION_PER_SELECTED_TAKE",
        )
        self.assertFalse(capture["capture"]["post_conversion_best_of_n"])
        self.assertFalse(capture["capture"]["second_pass"])
        self.assertEqual(
            capture["capture"]["post_conversion_processing"],
            ["constant_level_alignment_only"],
        )

    def test_h2_sidecar_does_not_claim_stream2_hold(self):
        p6 = self.load(SIDECAR)["p6_ulysse_emotional"]
        self.assertEqual(p6["state"], STATE)
        self.assertEqual(p6["human_state"], "PASS")
        self.assertEqual(p6["casting_state"], "CLOSED")
        self.assertEqual(p6["stream2_state"], "EXIT_CRITICAL_PATH")
        self.assertEqual(p6["exact_segments"], EXPECTED_SEGMENTS)


if __name__ == "__main__":
    unittest.main()
