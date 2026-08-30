import unittest

from tools.ci_changes import classify


class ChangeRoutingTests(unittest.TestCase):
    def test_production_plan_metadata_is_cheap_only(self):
        result = classify([
            "series/orleans-cathedral/production-plan/orleans-cathedral-ep01.plan.json",
            "docs/PRODUCTION_PLAN_V1.md",
            "tests/test_production_plan.py",
        ])
        self.assertFalse(result["audio_needed"])
        self.assertFalse(result["build_needed"])

    def test_pages_workflow_change_rebuilds_without_audio(self):
        result = classify([
            ".github/workflows/pages.yml",
            "tools/ci_changes.py",
            "tests/test_ci_changes.py",
        ])
        self.assertFalse(result["audio_needed"])
        self.assertTrue(result["build_needed"])

    def test_program_change_requires_audio_and_build(self):
        result = classify(["series/orleans-cathedral/audio/orleans-cathedral-ep01.json"])
        self.assertTrue(result["audio_needed"])
        self.assertTrue(result["build_needed"])

    def test_direction_and_sound_requirements_require_audio(self):
        result = classify([
            "series/orleans-cathedral/direction/orleans-cathedral-ep08.direction.json",
            "series/orleans-cathedral/sound-requirements.json",
        ])
        self.assertTrue(result["audio_needed"])
        self.assertTrue(result["build_needed"])

    def test_legacy_production_strategy_change_requires_audio(self):
        result = classify(["tools/production.py"])
        self.assertTrue(result["audio_needed"])
        self.assertTrue(result["build_needed"])

    def test_site_only_change_can_build_without_audio(self):
        result = classify(["web/app.js", "series/orleans-cathedral/series.json"])
        self.assertFalse(result["audio_needed"])
        self.assertTrue(result["build_needed"])
    def test_deploy_condition_survives_skipped_audio_chain(self):
        workflow = open(".github/workflows/pages.yml", encoding="utf-8").read()
        self.assertIn(
            "if: always() && github.event_name != 'pull_request' && "
            "needs.changes.outputs.build_needed == 'true' && needs.build.result == 'success'",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
