import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "web" / "next-step.js"
CAPABILITY_PATH = ROOT / "series" / "seville-discovery-v2" / "AUDIO_FIRST_UX_CAPABILITY.json"


class AudioFirstUxContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT_PATH.read_text(encoding="utf-8")
        cls.capability = json.loads(CAPABILITY_PATH.read_text(encoding="utf-8"))

    def test_activation_is_explicit_and_fail_safe(self):
        runtime = self.capability["runtime"]
        self.assertEqual(runtime["visit_experience_capability"], "audio_first_field_ui")
        self.assertEqual(
            runtime["activation"],
            {
                "enabled": True,
                "version": 2,
                "classic_fallback_url": "../seville-discovery/",
            },
        )
        self.assertIn("config.enabled !== true", self.script)
        self.assertIn("Number(config.version) !== 2", self.script)
        self.assertIn("classic_fallback_url", self.script)
        self.assertIn("audioFirst ? setupAudioFirst() : enhanceLegacy()", self.script)

    def test_primary_field_surface_is_minimal_and_complete(self):
        required = (
            "Étape ${index + 1}/${episodes.length}",
            "data-audio-first-toggle",
            "Itinéraire",
            "data-audio-first-arrived",
            "J’y suis",
            "data-audio-first-continue",
            "Continuer",
        )
        for marker in required:
            self.assertIn(marker, self.script)
        self.assertIn("primaryCue(episode, field)", self.script)
        self.assertIn("concise(cue, 180)", self.script)
        self.assertIn("concise(episode.stop || episode.location || episode.title, 100)", self.script)

    def test_deep_content_stays_secondary(self):
        for label in (
            "Je ne trouve pas",
            "Approfondir",
            "Transcription",
            "Sources",
            "Toutes les étapes",
            "Version classique V1",
        ):
            self.assertIn(label, self.script)
        self.assertIn('class="audio-first-more"', self.script)
        self.assertIn('#app.audio-first-v2 .episodes,', self.script)
        self.assertIn('.episodes[data-audio-first-details-open="1"]', self.script)

    def test_audio_first_reuses_shared_player_instead_of_owning_playback(self):
        self.assertIn("playerToggle.click()", self.script)
        self.assertIn("querySelector('[data-play]')?.click()", self.script)
        self.assertNotRegex(self.script, r"playerAudio\.src\s*=")
        self.assertNotRegex(self.script, r"playerAudio\.play\s*\(")
        self.assertNotRegex(self.script, r"playerAudio\.pause\s*\(")

    def test_v1_fallback_is_declared_and_runtime_driven(self):
        self.assertEqual(
            self.capability["integration"]["required_visit_experience_fragment"]["capabilities"]["audio_first_field_ui"]["classic_fallback_url"],
            "../seville-discovery/",
        )
        self.assertIn('href="${esc(audioFirst.classic_fallback_url)}"', self.script)
        # The shared runtime must not special-case the Seville V1 slug.
        script_without_contract_key = self.script.replace("classic_fallback_url", "")
        self.assertNotIn("seville-discovery", script_without_contract_key)

    def test_capability_contract_carries_acceptance_invariants(self):
        invariants = set(self.capability["invariants"])
        self.assertIn("V1_CHANGED_FILES=0", invariants)
        self.assertIn("non-V2 series do not activate audio-first mode without the explicit capability", invariants)
        self.assertIn("classic V1 remains reachable from the V2 overflow", invariants)


if __name__ == "__main__":
    unittest.main()
