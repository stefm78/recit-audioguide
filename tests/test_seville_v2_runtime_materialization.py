import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "series" / "seville-discovery-v2"
SERIES_PATH = V2 / "series.json"
EXPERIENCE_PATH = V2 / "assets" / "visit-experience.json"
AUDIO_MANIFEST_PATH = V2 / "runtime-audio-manifest.json"
AUDIO_ROOT = V2 / "assets" / "audio"

EXPECTED_IDS = (
    [f"SEV2-FRI-AM-{i:02d}" for i in range(1, 9)]
    + [f"SEV2-SAT-{i:02d}" for i in range(1, 9)]
    + [f"SEV2-SUN-{i:02d}" for i in range(1, 10)]
)


class SevilleV2RuntimeMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = json.loads(SERIES_PATH.read_text(encoding="utf-8"))
        cls.experience = json.loads(EXPERIENCE_PATH.read_text(encoding="utf-8"))
        cls.audio_manifest = json.loads(AUDIO_MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_exact_25_scene_runtime_graph(self):
        ids = [episode["id"] for episode in self.series["episodes"]]
        self.assertEqual(ids, EXPECTED_IDS)
        self.assertEqual(len(set(ids)), 25)
        self.assertEqual(set(self.experience["episodes"]), set(EXPECTED_IDS))

    def test_audio_first_activation_and_v1_fallback(self):
        config = self.experience["capabilities"]["audio_first_field_ui"]
        self.assertEqual(config, {
            "enabled": True,
            "version": 2,
            "classic_fallback_url": "../seville-discovery/",
        })

    def test_sunday_primary_sequence_and_fallback_only_pilatos(self):
        sunday = [episode for episode in self.series["episodes"] if episode["id"].startswith("SEV2-SUN-")]
        self.assertEqual([e["id"] for e in sunday], [f"SEV2-SUN-{i:02d}" for i in range(1, 10)])
        self.assertIn("Maestranza", sunday[0]["stop"])
        self.assertIn("Lockers Agua", sunday[3]["stop"])
        self.assertIn("Bellas Artes", sunday[4]["stop"])
        self.assertTrue(all("Casa de Pilatos" not in json.dumps(e, ensure_ascii=False) for e in sunday))
        policy = self.series["visit"]["sunday_policy"]
        self.assertEqual(policy["casa_de_pilatos"], "FALLBACK_ONLY")
        self.assertEqual(
            policy["primary_sequence"],
            ["MAESTRANZA", "CHECKOUT_LOCKERS_SILENCE", "BELLAS_ARTES", "PROTECTED_AIRPORT_DEPARTURE"],
        )

    def test_route_links_exist_for_all_25_scenes(self):
        for episode in self.series["episodes"]:
            self.assertTrue(episode["maps_url"].startswith("https://www.google.com/maps/"), episode["id"])

    def test_primary_text_budget_is_enforced_by_j3_runtime(self):
        for scene_id, field in self.experience["episodes"].items():
            self.assertLessEqual(len(field["look_first"]), 180, scene_id)
        next_step = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8")
        self.assertIn("return concise(cue, 180);", next_step)
        self.assertIn("concise(episode.stop || episode.location || episode.title, 100)", next_step)

    def test_25_qualified_audio_assets_are_exact_and_complete(self):
        entries = {entry["scene_id"]: entry for entry in self.audio_manifest["entries"]}
        self.assertEqual(set(entries), set(EXPECTED_IDS))
        self.assertEqual(self.audio_manifest["hash_match_count"], 25)
        for scene_id in EXPECTED_IDS:
            scene_dir = AUDIO_ROOT / scene_id
            audio = scene_dir / "audio.mp3"
            renderer_manifest = scene_dir / "manifest.json"
            transcript = scene_dir / "transcript.json"
            self.assertTrue(audio.is_file(), scene_id)
            self.assertTrue(renderer_manifest.is_file(), scene_id)
            self.assertTrue(transcript.is_file(), scene_id)
            entry = entries[scene_id]
            self.assertTrue(entry["audio_sha256_match"], scene_id)
            self.assertEqual(hashlib.sha256(audio.read_bytes()).hexdigest(), entry["audio_sha256_expected_j4"], scene_id)
            self.assertEqual(hashlib.sha256(audio.read_bytes()).hexdigest(), entry["audio_sha256_published_source"], scene_id)
            self.assertEqual(hashlib.sha256(renderer_manifest.read_bytes()).hexdigest(), entry["renderer_manifest_sha256"], scene_id)
            self.assertEqual(hashlib.sha256(transcript.read_bytes()).hexdigest(), entry["transcript_sha256"], scene_id)

    def test_series_audio_urls_resolve_to_packaged_assets(self):
        by_id = {episode["id"]: episode for episode in self.series["episodes"]}
        for scene_id in EXPECTED_IDS:
            episode = by_id[scene_id]
            prefix = f"../../data/seville-discovery-v2/assets/audio/{scene_id}/"
            self.assertEqual(episode["audio_policy"], "packaged_sha256")
            self.assertEqual(episode["audio_url"], prefix + "audio.mp3")
            self.assertEqual(episode["transcript_url"], prefix + "transcript.json")
            self.assertEqual(episode["audio_manifest_url"], prefix + "manifest.json")

    def test_shared_player_resume_and_media_session_contract_is_preserved(self):
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        required = (
            "function saveProgress()",
            "function restore(s)",
            "localStorage.setItem(`recit:${series.slug}`",
            "function nativeMediaSession()",
            "Plugins?.MediaSession",
            "navigator.mediaSession.setActionHandler('play'",
            "navigator.mediaSession.setActionHandler('pause'",
            "native.setPositionState(payload)",
            "navigator.mediaSession.setPositionState(payload)",
        )
        for marker in required:
            self.assertIn(marker, app)

    def test_j3_audio_first_contract_is_consumed_without_shared_ux_change(self):
        next_step = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8")
        self.assertIn("../../data/${encodeURIComponent(slug)}/assets/visit-experience.json", next_step)
        self.assertIn("audio_first_field_ui", next_step)
        self.assertIn("classic_fallback_url", next_step)
        self.assertIn("return audioFirst ? setupAudioFirst() : enhanceLegacy();", next_step)

    def test_static_build_materializes_self_contained_v2_audio(self):
        subprocess.run(["python", "site/build.py"], cwd=ROOT, check=True)
        dist = ROOT / "dist"
        self.assertTrue((dist / "s" / "seville-discovery-v2" / "index.html").is_file())
        published = json.loads((dist / "data" / "seville-discovery-v2" / "series.json").read_text(encoding="utf-8"))
        self.assertEqual(published["state"], "ready")
        self.assertTrue((dist / "data" / "seville-discovery-v2" / "assets" / "visit-experience.json").is_file())
        for episode in published["episodes"]:
            scene_id = episode["id"]
            self.assertEqual(episode["audio_source"], "packaged")
            self.assertTrue((dist / "data" / "seville-discovery-v2" / "assets" / "audio" / scene_id / "audio.mp3").is_file())
            self.assertTrue(episode["audio_url"].startswith("../../data/seville-discovery-v2/assets/audio/"))
        self.assertEqual(len(list((dist / "data" / "seville-discovery-v2" / "assets" / "audio").glob("*/audio.mp3"))), 25)


if __name__ == "__main__":
    unittest.main()
