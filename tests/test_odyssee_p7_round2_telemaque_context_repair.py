import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import p7_round2_telemaque_context_repair as repair


class P7Round2TelemaqueContextRepairTests(unittest.TestCase):
    def test_materialize_is_father_only_and_preserves_round2_ulysse(self):
        out = repair.ROOT / "generated" / "p7-r2-telemaque-repair-test"
        try:
            plan = repair.materialize(out)
            self.assertEqual(
                plan["status"],
                "READY_TO_RENDER_P7_R2_FATHER_CONTEXT_REPAIR",
            )
            self.assertEqual(plan["range"], {"start_segment": 136, "end_segment": 154})
            self.assertEqual(
                [item["segment"] for item in plan["telemaque_snapshot"]],
                list(repair.TELEMAQUE_SEGMENTS),
            )
            self.assertEqual(len(plan["ulysse_round2_snapshot"]), 9)
            self.assertFalse(plan["repair"]["ulysse_artistic_parameter_change"])
            self.assertFalse(plan["repair"]["recasting"])
            self.assertFalse(plan["repair"]["frozen_text_change"])
            self.assertFalse(plan["repair"]["provider_change"])
            self.assertFalse(plan["repair"]["new_edge_tuning"])
            self.assertFalse(plan["repair"]["round3_edge"])

            program = json.loads(
                (repair.ROOT / plan["program_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(len(program["segments"]), 19)
            by_abs = {
                136 + offset: segment
                for offset, segment in enumerate(program["segments"])
            }
            for number in repair.TELEMAQUE_SEGMENTS:
                segment = by_abs[number]
                self.assertEqual(segment["speaker"], "TÉLÉMAQUE")
                self.assertEqual(segment["preset"], "odyssee-telemaque")
                self.assertEqual(segment["language_locale"], "fr-FR")
                self.assertNotIn("rate", segment)
                self.assertNotIn("pitch", segment)
                self.assertNotIn("volume", segment)

            for expected in plan["ulysse_round2_snapshot"]:
                segment = by_abs[expected["segment"]]
                self.assertEqual(segment["rate"], expected["rate"])
                self.assertEqual(segment["pitch"], expected["pitch"])
                self.assertEqual(segment["volume"], expected["volume"])
                self.assertEqual(
                    segment["pause_after_ms"],
                    expected["pause_after_ms"],
                )
        finally:
            if out.exists():
                shutil.rmtree(out)

    def _resolved_transcript(self, plan):
        program = json.loads(
            (repair.ROOT / plan["program_path"]).read_text(encoding="utf-8")
        )
        voices = json.loads(
            (repair.ROOT / plan["voice_pack_path"]).read_text(encoding="utf-8")
        )
        presets = {item["id"]: item for item in voices["presets"]}
        resolved = []
        for segment in program["segments"]:
            item = dict(segment)
            preset = presets[item["preset"]]
            item["voice"] = item.get("voice", preset["voice"])
            item["rate"] = item.get("rate", preset.get("rate", "+0%"))
            item["pitch"] = item.get("pitch", preset.get("pitch", "+0Hz"))
            item["volume"] = item.get("volume", preset.get("volume", "+0%"))
            item["provider"] = item.get(
                "provider",
                preset.get("provider", "edge"),
            )
            resolved.append(item)
        return {"segments": resolved}

    def test_collect_accepts_exact_transport_and_rejects_ulysse_drift(self):
        materialized = (
            repair.ROOT / "generated" / "p7-r2-telemaque-repair-collect-test"
        )
        try:
            plan = repair.materialize(materialized)
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plan_path = root / "plan.json"
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                render_root = root / "renders"
                render_dir = render_root / plan["program_id"]
                render_dir.mkdir(parents=True)
                (render_dir / "audio.mp3").write_bytes(b"repair-audio")
                (render_dir / "qa-report.json").write_text(
                    json.dumps({"status": "PASS"}),
                    encoding="utf-8",
                )
                (render_dir / "manifest.json").write_text(
                    json.dumps({"status": "success"}),
                    encoding="utf-8",
                )
                transcript = self._resolved_transcript(plan)
                (render_dir / "transcript.json").write_text(
                    json.dumps(transcript, ensure_ascii=False),
                    encoding="utf-8",
                )

                release = root / "release"
                index = repair.collect(
                    plan_path,
                    render_root,
                    release,
                    "a" * 40,
                )
                self.assertEqual(
                    index["status"],
                    "machine-ready-p7-r2-father-context-repair",
                )
                self.assertFalse(index["ulysse_artistic_parameter_change"])
                self.assertFalse(index["recasting"])
                self.assertFalse(index["frozen_text_change"])
                self.assertFalse(index["provider_change"])
                self.assertFalse(index["new_edge_tuning"])
                self.assertFalse(index["round3_edge"])
                self.assertEqual(
                    sorted(path.name for path in release.iterdir()),
                    sorted(
                        [
                            repair.REPAIR_AUDIO,
                            repair.REPAIR_QA,
                            repair.REPAIR_INDEX,
                        ]
                    ),
                )

                bad = self._resolved_transcript(plan)
                bad["segments"][0]["rate"] = "+99%"
                (render_dir / "transcript.json").write_text(
                    json.dumps(bad, ensure_ascii=False),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    repair.RepairError,
                    "rendered Ulysse drift",
                ):
                    repair.collect(
                        plan_path,
                        render_root,
                        root / "bad-release",
                        "b" * 40,
                    )
        finally:
            if materialized.exists():
                shutil.rmtree(materialized)


if __name__ == "__main__":
    unittest.main()
