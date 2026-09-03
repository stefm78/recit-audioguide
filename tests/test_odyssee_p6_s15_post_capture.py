import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools import p6_s15_post_capture as post


class P6S15PostCaptureTests(unittest.TestCase):
    def make_conversion_set(self, root):
        root = Path(root)
        converted = root / "converted"
        reports = root / "reports"
        converted.mkdir()
        reports.mkdir()
        results = []
        for segment in post.EXPECTED_SEGMENTS:
            output = converted / f"p6-s15-{segment}-ulysse.wav"
            output.write_bytes(f"converted-{segment}".encode("utf-8"))
            results.append({
                "segment": segment,
                "state": "CONVERTED_EXACTLY_ONCE",
                "output_path": str(output),
                "output_sha256": post.sha256_file(output),
                "report_path": str(reports / f"p6-s15-{segment}.json"),
            })
        data = {
            "schema": "recit.odyssee.p6.s15.private_conversion_set.v1",
            "status": "P6_S15_12_OF_12_BELTOUT_MACHINE_PASS",
            "segments": list(post.EXPECTED_SEGMENTS),
            "engine_ref": post.ENGINE_REF,
            "beltout_revision": "f71295e33cc9c0092083089ed0f9c1a532e77e6b",
            "results": results,
        }
        path = root / "conversion-set.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path, data

    def test_stage_publishes_only_converted_audio_and_routes_performance_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            conversion_path, conversion = self.make_conversion_set(root)
            out = root / "stage"
            result = post.stage(conversion_path, out)

            self.assertEqual(result["status"], "P6_S15_POST_CAPTURE_STAGE_READY")
            self.assertFalse(result["contains_raw_human_audio"])
            self.assertFalse(result["contains_private_source_paths"])

            archive = Path(result["publishable_archive"])
            with tarfile.open(archive, "r:xz") as tf:
                names = sorted(tf.getnames())
            self.assertEqual(
                names,
                sorted(
                    ["p6-converted-index.json"]
                    + [
                        f"clips/p6-s15-{segment}-ulysse.wav"
                        for segment in post.EXPECTED_SEGMENTS
                    ]
                ),
            )
            self.assertTrue(all("raw" not in name.lower() for name in names))

            staged_root = Path(result["staged_product_root"])
            s15 = json.loads(
                (staged_root / "series/odyssee/programs/S15.json").read_text(
                    encoding="utf-8"
                )
            )
            for segment in post.EXPECTED_SEGMENTS:
                item = s15["segments"][segment - 1]
                self.assertEqual(item["speaker"], "ULYSSE")
                self.assertEqual(
                    item["performance_provider"],
                    "immutable-voice-clips-v1",
                )
                self.assertEqual(
                    item["provider_parameters"]["reference"],
                    f"p6-s15-{segment}",
                )
            self.assertNotIn(
                "performance_provider",
                s15["segments"][122],
            )

            manifest = json.loads(
                (
                    staged_root
                    / "series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["engine_ref"], post.ENGINE_REF)
            unit = next(x for x in manifest["units"] if x["id"] == "S15")
            self.assertEqual(unit["state"], "ready")
            self.assertIn("immutable-voice-clips-v1", unit["providers"])
            self.assertNotIn("hold_reason", unit)

            provider = json.loads(
                (
                    staged_root
                    / post.PUBLIC_PROVIDER_PACKAGE
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                provider["provider"]["id"],
                "immutable-voice-clips-v1",
            )
            self.assertEqual(len(provider["references"]), 12)
            self.assertTrue(
                all(
                    ref["source"]["type"] == "github_release_archive"
                    and ref["source"]["tag"] == post.RELEASE_TAG
                    for ref in provider["references"]
                )
            )

            workflow = (
                staged_root / ".github/workflows/odyssee-production.yml"
            ).read_text(encoding="utf-8")
            self.assertIn(post.ENGINE_REF, workflow)
            self.assertIn('["S09","S15"]', workflow)

            private_needles = {
                str(Path(item["output_path"]).parent)
                for item in conversion["results"]
            }
            for path in [
                out / "publishable/p6-converted-index.json",
                staged_root / "series/odyssee/programs/S15.json",
                staged_root / post.PUBLIC_PROVIDER_PACKAGE,
                staged_root
                / "series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json",
            ]:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn('"private_source_path"', text)
                for needle in private_needles:
                    self.assertNotIn(needle, text)

    def test_report_validation_rejects_retry_or_artistic_processing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "out.wav"
            output.write_bytes(b"converted")
            slot = {
                "segment": 112,
                "source_sha256": "1" * 64,
                "seed": 202609060112,
            }
            package = {
                "model": {
                    "revision": "f71295e33cc9c0092083089ed0f9c1a532e77e6b"
                }
            }
            report = {
                "status": "PASS",
                "retry_allowed_after_output": True,
                "network_used": False,
                "inputs": {
                    "source_sha256": slot["source_sha256"],
                    "target_reference_sha256": post.ANCHOR_SHA256,
                    "beltout_revision": package["model"]["revision"],
                },
                "conversion": {
                    "seed": slot["seed"],
                    "n_timesteps": 10,
                    "best_of_n": False,
                    "second_pass": False,
                    "time_stretch": False,
                    "pitch_shift": False,
                    "emotion_dsp": False,
                },
                "output": {"sha256": post.sha256_file(output)},
                "evidence": {
                    "pass": True,
                    "audio_decode": {
                        "persistent_normalized_raw_file": False,
                        "filters": [],
                    },
                },
            }
            report_path = root / "report.json"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                post.P6PostCaptureError,
                "retry prohibition",
            ):
                post._validate_report(report_path, output, slot, package)


if __name__ == "__main__":
    unittest.main()
