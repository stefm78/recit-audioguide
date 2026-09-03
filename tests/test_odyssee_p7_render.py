import json
import tempfile
import unittest
from pathlib import Path

from tools import p7_render as p7


class P7Round1RenderTests(unittest.TestCase):
    def test_b_variant_changes_only_ulysse_profile_and_explicit_pauses(self):
        window = {
            "id": "state",
            "ulysse_segments": [10, 12],
            "B": {
                "ulysse": {
                    "voice": "fr-FR-HenriNeural",
                    "rate": "-1%",
                    "pitch": "-8Hz",
                    "volume": "+3%",
                },
                "ulysse_pause_after_ms": {"10": 180, "12": 320},
            },
        }
        source = {
            "schema_version": 6,
            "id": "source",
            "title": "Source",
            "language": "fr-FR",
            "profile": "speech",
            "sources": [],
            "segments": [
                {"speaker": "ULYSSE", "text": "A", "preset": "odyssee-ulysse"},
                {"speaker": "AUTRE", "text": "B", "preset": "other"},
                {"speaker": "ULYSSE", "text": "C", "preset": "odyssee-ulysse"},
            ],
        }
        voices = {
            "presets": [
                {
                    "id": "odyssee-ulysse",
                    "voice": "fr-FR-HenriNeural",
                    "rate": "-4%",
                    "pitch": "-10Hz",
                    "volume": "+2%",
                    "provider": "edge",
                },
                {
                    "id": "other",
                    "voice": "fr-FR-DeniseNeural",
                    "rate": "+1%",
                    "pitch": "+0Hz",
                    "volume": "+0%",
                    "provider": "edge",
                },
            ]
        }
        validated = {
            "start": 10,
            "end": 12,
            "program": source,
            "voice_pack": voices,
        }

        a_program, a_voices = p7.build_variant(window, validated, "A")
        b_program, b_voices = p7.build_variant(window, validated, "B")

        self.assertEqual(a_program["segments"], source["segments"])
        self.assertEqual(a_voices, voices)
        self.assertEqual(
            p7._preset_map(b_voices)["other"],
            p7._preset_map(voices)["other"],
        )
        directed = p7._preset_map(b_voices)["odyssee-ulysse"]
        self.assertEqual(directed["voice"], "fr-FR-HenriNeural")
        self.assertEqual(directed["rate"], "-1%")
        self.assertEqual(directed["pitch"], "-8Hz")
        self.assertEqual(directed["volume"], "+3%")
        self.assertEqual(b_program["segments"][0]["pause_after_ms"], 180)
        self.assertNotIn("pause_after_ms", b_program["segments"][1])
        self.assertEqual(b_program["segments"][2]["pause_after_ms"], 320)
        self.assertEqual(b_program["acoustic_space"], "dry")

    def test_collect_emits_only_machine_ready_review_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            render_root = root / "renders"
            release_out = root / "release"
            entries = []
            for index in range(8):
                program_id = f"p7-{index}"
                render_dir = render_root / program_id
                render_dir.mkdir(parents=True)
                (render_dir / "audio.mp3").write_bytes(f"audio-{index}".encode())
                (render_dir / "manifest.json").write_text(
                    json.dumps({"id": program_id}), encoding="utf-8"
                )
                (render_dir / "qa-report.json").write_text(
                    json.dumps({"status": "PASS"}), encoding="utf-8"
                )
                state = p7.EXPECTED_WINDOWS[index // 2]
                variant = "A" if index % 2 == 0 else "B"
                entries.append({
                    "state": state,
                    "variant": variant,
                    "program_id": program_id,
                    "source_program": f"series/{state}.json",
                    "source_program_git_blob_sha1": "a" * 40,
                    "production_voice_pack": "series/voices.json",
                    "production_voice_pack_sha256": "b" * 64,
                    "output_asset": f"{program_id}.mp3",
                    "qa_asset": f"{program_id}.qa-report.json",
                })

            plan = {
                "status": "READY_TO_RENDER_P7_ROUND1",
                "entry_count": 8,
                "engine_ref": p7.ENGINE_REF,
                "authority_contract": "series/p7.json",
                "authority_contract_sha256": "c" * 64,
                "entries": entries,
            }
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            index = p7.collect(
                plan_path,
                render_root,
                release_out,
                product_sha="d" * 40,
            )

            self.assertEqual(index["status"], "machine-ready-p7-review-assets")
            self.assertEqual(index["asset_count"], 16)
            self.assertFalse(index["production_programs_mutated"])
            self.assertFalse(index["decorative_sound"])
            self.assertEqual(
                sorted(p.name for p in release_out.iterdir()),
                sorted(
                    ["p7-review-index.json"]
                    + [entry["output_asset"] for entry in entries]
                    + [entry["qa_asset"] for entry in entries]
                ),
            )


if __name__ == "__main__":
    unittest.main()
