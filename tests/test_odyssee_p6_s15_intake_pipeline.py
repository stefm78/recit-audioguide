import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools import p6_s15_pipeline as p6


class P6S15IntakePipelineTests(unittest.TestCase):
    def make_capture_zip(self, root, mutate=None, extra_member=None):
        root = Path(root)
        contract, targets, _ = p6.validate_authorities()
        files = {}
        slots = []
        for segment in p6.EXPECTED_SEGMENTS:
            target = targets[segment]
            name = f"s15-{segment}.webm"
            data = f"synthetic-private-human-take-{segment}".encode("utf-8")
            digest = hashlib.sha256(data).hexdigest()
            files[name] = data
            slots.append({
                "segment": segment,
                "text": target["text"],
                "group": target["group"],
                "intent": target["intent"],
                "filename": name,
                "mime": "audio/webm",
                "duration_seconds": 1.5,
                "sha256": digest,
                "selected_before_conversion": True,
                "clean_capture_confirmed": True,
            })

        manifest = {
            "schema": p6.CAPTURE_SCHEMA,
            "status": p6.CAPTURE_STATUS,
            "segment_count": 12,
            "segments": list(p6.EXPECTED_SEGMENTS),
            "freeze_rule": contract["capture"]["selected_take_rule"],
            "post_freeze": {
                "conversion": "EXACTLY_ONE_BELTOUT_CONVERSION_PER_SELECTED_TAKE",
                "best_of_n": False,
                "second_pass": False,
                "post_conversion_processing": ["constant_level_alignment_only"],
            },
            "raw_human_voice_repository_policy": p6.RAW_POLICY,
            "slots": slots,
        }
        if mutate:
            mutate(manifest, files)

        manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        sums = [
            f"{hashlib.sha256(data).hexdigest()}  {name}"
            for name, data in files.items()
        ]
        sums.append(
            f"{hashlib.sha256(manifest_bytes).hexdigest()}  recording-manifest.json"
        )

        path = root / "capture.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as zf:
            for name, data in files.items():
                zf.writestr(name, data)
            zf.writestr("recording-manifest.json", manifest_bytes)
            zf.writestr("SHA256SUMS.txt", "\n".join(sums) + "\n")
            zf.writestr("README.txt", "private production capture\n")
            if extra_member:
                zf.writestr(extra_member, b"unexpected")
        return path

    def test_valid_12_of_12_capture_freezes_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = self.make_capture_zip(root)
            private_out = root / "private"
            frozen, plan = p6.intake(zip_path, private_out)

            self.assertEqual(
                frozen["status"],
                "FROZEN_12_OF_12_READY_FOR_SINGLE_BELTOUT_CONVERSION",
            )
            self.assertEqual(len(frozen["slots"]), 12)
            self.assertEqual(
                [x["segment"] for x in frozen["slots"]],
                list(p6.EXPECTED_SEGMENTS),
            )
            self.assertTrue((private_out / "FREEZE.lock").is_file())
            self.assertTrue((private_out / "conversion-plan.json").is_file())
            self.assertEqual(
                plan["status"],
                "READY_FOR_EXACTLY_ONE_CONVERSION_PER_FROZEN_TAKE",
            )
            self.assertTrue(
                all(x["conversion_ordinal"] == 1 for x in plan["slots"])
            )
            self.assertTrue(
                all(x["allow_retry_after_audio_output_exists"] is False for x in plan["slots"])
            )
            self.assertTrue(
                all(
                    x["post_conversion_processing"] == ["constant_level_alignment_only"]
                    for x in plan["slots"]
                )
            )

    def test_repo_local_private_workspace_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = self.make_capture_zip(Path(tmp))
            with self.assertRaisesRegex(
                p6.P6IntakeError,
                "must be outside the public repository checkout",
            ):
                p6.intake(zip_path, p6.ROOT / "generated" / "raw-human-audio")

    def test_missing_slot_is_rejected(self):
        def mutate(manifest, files):
            removed = manifest["slots"].pop()
            manifest["segment_count"] = 11
            manifest["segments"] = manifest["segments"][:-1]
            files.pop(removed["filename"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = self.make_capture_zip(root, mutate=mutate)
            with self.assertRaises(p6.P6IntakeError):
                p6.intake(zip_path, root / "private")

    def test_audio_hash_mismatch_is_rejected(self):
        def mutate(manifest, files):
            first = manifest["slots"][0]
            first["sha256"] = "0" * 64

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = self.make_capture_zip(root, mutate=mutate)
            with self.assertRaisesRegex(p6.P6IntakeError, "audio SHA-256 mismatch"):
                p6.intake(zip_path, root / "private")

    def test_unexpected_zip_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = self.make_capture_zip(root, extra_member="extra.txt")
            with self.assertRaisesRegex(p6.P6IntakeError, "unexpected members"):
                p6.intake(zip_path, root / "private")

    def test_frozen_source_drift_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = self.make_capture_zip(root)
            private_out = root / "private"
            frozen, _ = p6.intake(zip_path, private_out)
            first = Path(frozen["slots"][0]["private_source_path"])
            first.write_bytes(first.read_bytes() + b"drift")
            with self.assertRaisesRegex(p6.P6IntakeError, "hash drift"):
                p6.verify_frozen(private_out / "frozen-intake.json")


if __name__ == "__main__":
    unittest.main()
