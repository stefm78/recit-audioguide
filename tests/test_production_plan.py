import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import production_plan


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "series" / "orleans-cathedral" / "production-plan" / "orleans-cathedral-ep01.plan.json"
PROGRAM = ROOT / "series" / "orleans-cathedral" / "audio" / "orleans-cathedral-ep01.json"


class ProductionPlanTests(unittest.TestCase):
    def test_real_audioguide_plan_validates_without_rendering(self):
        summary = production_plan.validate_plan(PLAN)
        self.assertEqual(summary["status"], "valid")
        self.assertEqual(summary["id"], "orleans-cathedral-ep01")
        self.assertEqual(summary["mode"], "program-ref")
        self.assertEqual(summary["program_git_blob_sha1"], "9ed3f6552cf997e57c6a4a33e3c4696015d2debb")
        self.assertEqual(summary["segments"], 7)
        self.assertEqual(summary["overlays"], 5)

    def test_plan_contains_no_spoken_text(self):
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        self.assertFalse(production_plan.contains_key(plan, "text"))

    def test_program_blob_is_exact_authority(self):
        self.assertEqual(
            production_plan.git_blob_sha1(PROGRAM),
            "9ed3f6552cf997e57c6a4a33e3c4696015d2debb",
        )

    def test_drift_is_fail_fast(self):
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        drifted = copy.deepcopy(plan)
        drifted["content_binding"]["git_blob_sha1"] = "0" * 40
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake = tmp_path / "fake.plan.json"
            fake.write_text(json.dumps(drifted, ensure_ascii=False), encoding="utf-8")
            with mock.patch.object(production_plan, "ROOT", ROOT):
                with self.assertRaisesRegex(ValueError, "Program blob drift"):
                    production_plan.resolve_program(fake, drifted)


if __name__ == "__main__":
    unittest.main()
