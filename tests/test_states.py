import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import production


def load_site_builder():
    path = production.ROOT / "site" / "build.py"
    spec = importlib.util.spec_from_file_location("recit_site_build", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


site_build = load_site_builder()


class ProductionStateTests(unittest.TestCase):
    def make_sources(self):
        temp = tempfile.TemporaryDirectory(dir=production.ROOT)
        root = Path(temp.name)
        (root / "ready.json").write_text('{"id":"test-ready"}', encoding="utf-8")
        (root / "failed.json").write_text('{"id":"test-failed"}', encoding="utf-8")
        return temp, root

    def test_partial_render_is_degradable_and_removes_stale_failed_output(self):
        temp, root = self.make_sources()
        try:
            out = root / "out"
            stale = out / "test-failed"
            stale.mkdir(parents=True)
            (stale / "audio.mp3").write_bytes(b"stale")

            def fake_render(source, output_root, sounds_path=None):
                if source.name == "failed.json":
                    raise RuntimeError("simulated render failure")
                return {
                    "source": str(source.relative_to(production.ROOT)),
                    "id": "test-ready",
                    "state": "ready",
                    "cache_hit": False,
                }

            with mock.patch.object(production, "production_specs", return_value=[]), \
                 mock.patch.object(production, "render_unmanaged", side_effect=fake_render):
                rc = production.run_all(str(root / "*.json"), out)

            report = json.loads((out / "render-report.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 0)
            self.assertEqual(report["status"], "partial")
            self.assertEqual(report["success_count"], 1)
            self.assertEqual(report["failure_count"], 1)
            self.assertEqual(report["failures"][0]["id"], "test-failed")
            self.assertEqual(report["failures"][0]["state"], "failed")
            self.assertFalse(stale.exists())
        finally:
            temp.cleanup()

    def test_wholly_failed_render_remains_fatal(self):
        temp, root = self.make_sources()
        try:
            out = root / "out"
            with mock.patch.object(production, "production_specs", return_value=[]), \
                 mock.patch.object(production, "render_unmanaged", side_effect=RuntimeError("boom")):
                rc = production.run_all(str(root / "*.json"), out)
            report = json.loads((out / "render-report.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 2)
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["failure_count"], 2)
        finally:
            temp.cleanup()


class PublicationStateTests(unittest.TestCase):
    def setUp(self):
        site_build.WARN.clear()

    def test_series_state_contract(self):
        self.assertEqual(site_build.series_state(["ready", "ready"]), "ready")
        self.assertEqual(site_build.series_state(["ready", "warning"]), "degraded")
        self.assertEqual(site_build.series_state(["ready", "failed"]), "degraded")
        self.assertEqual(site_build.series_state(["failed", "failed"]), "blocked")

    def test_episode_without_audio_is_failed(self):
        episode = {"id": "ep", "title": "Episode", "summary": "Résumé"}
        with mock.patch.object(site_build, "publish_generated_audio", return_value=False):
            state = site_build.classify_episode(episode, "story", "test", set())
        self.assertEqual(state, "failed")
        self.assertEqual(episode["state"], "failed")

    def test_failed_new_render_with_fallback_is_warning(self):
        episode = {
            "id": "ep",
            "title": "Episode",
            "summary": "Résumé",
            "audio_url": "https://example.invalid/previous.mp3",
        }
        with mock.patch.object(site_build, "publish_generated_audio", return_value=False):
            state = site_build.classify_episode(episode, "story", "test", {"ep"})
        self.assertEqual(state, "warning")
        self.assertEqual(episode["audio_source"], "fallback")

    def test_complete_episode_is_ready(self):
        episode = {
            "id": "ep",
            "title": "Episode",
            "summary": "Résumé",
            "audio_url": "https://example.invalid/audio.mp3",
        }
        with mock.patch.object(site_build, "publish_generated_audio", return_value=False):
            state = site_build.classify_episode(episode, "story", "test", set())
        self.assertEqual(state, "ready")


class PlayerUITests(unittest.TestCase):
    def test_player_markup_has_simple_controls(self):
        html = (production.ROOT / "web" / "series.html").read_text(encoding="utf-8")
        for element_id in ("player-back", "player-toggle", "player-forward", "player-seek", "player-current", "player-duration"):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("Reculer de 15 secondes", html)
        self.assertIn("Avancer de 15 secondes", html)

    def test_player_javascript_is_valid_and_keeps_media_session_seek(self):
        app = production.ROOT / "web" / "app.js"
        subprocess.run(["node", "--check", str(app)], check=True, capture_output=True, text=True)
        source = app.read_text(encoding="utf-8")
        self.assertIn("seekBy(-15)", source)
        self.assertIn("seekBy(15)", source)
        self.assertIn("seekbackward", source)
        self.assertIn("seekforward", source)


if __name__ == "__main__":
    unittest.main()
