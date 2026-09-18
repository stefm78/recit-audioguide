#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

TARGETS = {
    137: {
        "text": "Qui es-tu ?",
        "source_fingerprint": "b70f8b8fc753a078e9f947ba05cc50402f4d35bf55a5970fab07dac282157683",
        "clip_sha256": "469bada0e1c0778c260b3a3c0cb09543db5e1f21f3b2272d7b4f26cef95f40e8",
    },
    147: {
        "text": "Tous les hommes qui arrivent à Ithaque ont vu mon père. Certains ont bu avec lui. D’autres lui ont parlé hier. Et maintenant toi, tu es lui ?",
        "source_fingerprint": "6f81a258720cd3212d630827d6bd3284d698a7565b3445614d2bcddfda9af4f2",
        "clip_sha256": "58f3634efd84d270c091fb4624032d3596cfd223437f61a5ec5a893e41b86fd2",
    },
    153: {
        "text": "Tu ne peux pas entrer dans une pièce et dire ce mot comme si—",
        "source_fingerprint": "59954baa87b98d4d7005a5811335df587923b3fcc166ceec5766ad324ef66296",
        "clip_sha256": "f55e8c62e3c4dd63ad25ea9628bccda34b38ee92a43ecf5fd6e7fcba27115375",
    },
}

REFERENCE_SHA256 = "16e4067f6ab09ecb5a8b8afa9ef7b578ff16b80a01c9d5725d2eb0a2c606bc8f"
PACKAGE_SHA256 = "918b0acc9eae83b2bce8722504180d1a2841321602e0d11aee5d9076c11154e8"
ACCEPTED_AUDIO_SHA256 = "491ef48a0eed6f891f8226c7b4e6855fa4de3631ae9647794b6554852f0e7fae"
SOURCE_ARTIFACT = 9900070422
CACHE_ARTIFACT = 9900067012
RECOVERY_RUN = 33811580901
SOURCE_RUN = 33771590501
FIXED_SEED = 650100
PROVIDER = "chatterbox-multilingual-v3"
PRODUCT_PACKAGE = Path("series/odyssee/production/provider-packages/TELEMAQUE_CHATTERBOX_FR_REFERENCE_V1.json")
S12_PATH = Path("series/odyssee/programs/S12.json")
MANIFEST_PATH = Path("series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json")
AUTHORITY_PATH = Path("series/odyssee/review/TELEMAQUE_FRENCH_CLEAN_PATH_V1.json")
VOICE_PACK = Path("series/odyssee/production/voice-packs/ODYSSEE_PRODUCTION_V1.json")
BINDING_PATH = Path("series/odyssee/production/TELEMAQUE_S12_CACHE_ONLY_BINDING_V1.json")
TEST_PATH = Path("tests/test_odyssee_telemaque_s12_cache_only_binding.py")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def artifact_paths():
    source_root = Path(os.environ["TELEMAQUE_SOURCE_ROOT"])
    cache_root = Path(os.environ["TELEMAQUE_CACHE_ROOT"])
    source_package = source_root / "input/provider-package.json"
    source_reference = source_root / "input/reference/telemaque-p1-human-pass.wav"
    source_cache = cache_root / "render/.cache/voices"
    return source_package, source_reference, source_cache


def verify_source_artifacts():
    source_package, source_reference, source_cache = artifact_paths()
    assert source_package.is_file(), source_package
    assert sha(source_package) == PACKAGE_SHA256
    assert source_reference.is_file(), source_reference
    assert sha(source_reference) == REFERENCE_SHA256
    package = load(source_package)
    assert package["provider"]["id"] == PROVIDER
    assert int(package["synthesis"]["seed"]) == FIXED_SEED
    assert package["synthesis"]["parameters"] == {
        "language_id": "fr",
        "reference": "p1-telemaque-human-pass",
        "exaggeration": 0.34,
        "cfg_weight": 0.5,
        "temperature": 0.74,
    }
    assert package["references"] == [{
        "id": "p1-telemaque-human-pass",
        "path": "generated/telemaque-fr-clean/input/reference/telemaque-p1-human-pass.wav",
        "sha256": REFERENCE_SHA256,
    }]
    assert package["fallback"] == "fail"
    for sequence, target in TARGETS.items():
        clip = source_cache / f"{target['source_fingerprint']}.mp3"
        assert clip.is_file(), (sequence, clip)
        assert sha(clip) == target["clip_sha256"], sequence
    return source_package, source_reference, source_cache


def materialize():
    source_package, source_reference, _ = verify_source_artifacts()
    original_s12 = load(S12_PATH)
    original_manifest = load(MANIFEST_PATH)
    original_authority = load(AUTHORITY_PATH)

    assert original_authority["authority_issue"] == 178
    assert original_authority["diagnosis"]["further_edge_retry_authorized"] is False
    assert original_authority["product_decision"]["provider"] == PROVIDER
    assert original_authority["product_decision"]["probe"]["exact_segments"] == [137, 147, 153]

    # Freeze exact accepted provider-package bytes; do not rewrite/tune it.
    PRODUCT_PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_package, PRODUCT_PACKAGE)
    assert sha(PRODUCT_PACKAGE) == PACKAGE_SHA256

    # Materialize the exact accepted reference at the package-declared workspace path.
    runtime_reference = Path("generated/telemaque-fr-clean/input/reference/telemaque-p1-human-pass.wav")
    runtime_reference.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_reference, runtime_reference)
    assert sha(runtime_reference) == REFERENCE_SHA256

    s12 = json.loads(json.dumps(original_s12, ensure_ascii=False))
    original_targets = {}
    for sequence, expected in TARGETS.items():
        before = original_s12["segments"][sequence - 1]
        assert before["speaker"] == "TÉLÉMAQUE"
        assert before["character_id"] == "telemaque"
        assert before["preset"] == "odyssee-telemaque"
        assert before["text"] == expected["text"]
        assert "performance_provider" not in before
        assert "provider_seed" not in before
        original_targets[str(sequence)] = before
        after = s12["segments"][sequence - 1]
        after["performance_provider"] = PROVIDER
        after["provider_seed"] = FIXED_SEED

    # Hard invariant: every non-target S12 segment is byte-for-byte JSON-equivalent.
    for index, (before, after) in enumerate(zip(original_s12["segments"], s12["segments"]), start=1):
        if index not in TARGETS:
            assert before == after, index
    # Ulysse remains untouched even inside S12.
    for index, (before, after) in enumerate(zip(original_s12["segments"], s12["segments"]), start=1):
        if before.get("character_id") == "ulysse":
            assert before == after, f"Ulysse drift at S12:{index}"

    write(S12_PATH, s12)
    program_sha = sha(S12_PATH)

    manifest = json.loads(json.dumps(original_manifest, ensure_ascii=False))
    unit = next(item for item in manifest["units"] if item["id"] == "S12")
    assert unit["voice_pack"] == str(VOICE_PACK)
    voice_pack_sha = sha(VOICE_PACK)
    assert unit["voice_pack_sha256"] == voice_pack_sha
    unit["provider"] = "edge+chatterbox-multilingual-v3"
    unit["providers"] = ["edge", PROVIDER]
    unit["provider_packages"] = [{
        "provider": PROVIDER,
        "package": str(PRODUCT_PACKAGE),
        "package_sha256": PACKAGE_SHA256,
    }]
    unit["program_sha256"] = program_sha
    write(MANIFEST_PATH, manifest)

    authority = json.loads(json.dumps(original_authority, ensure_ascii=False))
    authority["status"] = "TELEMAQUE_FRENCH_CLEAN_PATH_HUMAN_PASS"
    authority["human_result"] = {
        "verdict": "TELEMAQUE_FRENCH_CLEAN_PATH_HUMAN_PASS",
        "release": "odyssee-telemaque-fr-clean-level-recovery-v1",
        "audio": "telemaque-fr-clean-probe-level-recovered.mp3",
        "audio_sha256": ACCEPTED_AUDIO_SHA256,
        "source_run": SOURCE_RUN,
        "source_artifact": SOURCE_ARTIFACT,
        "cache_artifact": CACHE_ARTIFACT,
        "level_only_recovery_run": RECOVERY_RUN,
        "resynthesis_during_recovery": False,
        "machine_qa": "PASS",
        "dimensions": {
            "french_fully_clean": "PASS",
            "p1_identity_continuity": "PASS",
            "credible_young_adult": "PASS",
            "natural_phrasing": "PASS",
            "distinct_from_ulysse": "PASS",
            "no_caricature": "PASS",
        },
    }
    authority.setdefault("post_pass", {})["integration"] = {
        "status": "S12_CACHE_ONLY_AUTHORIZED_PENDING_MACHINE_QA",
        "scene": "S12",
        "segments": [137, 147, 153],
        "provider": PROVIDER,
        "provider_package_sha256": PACKAGE_SHA256,
        "reference_sha256": REFERENCE_SHA256,
        "seed": FIXED_SEED,
        "resynthesis_forbidden": True,
        "cache_gate": {"target": 3, "required_hits": 3, "required_misses": 0},
    }
    write(AUTHORITY_PATH, authority)

    test_source = '''import hashlib\nimport json\nimport unittest\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\ndef load(path):\n    return json.loads((ROOT / path).read_text(encoding="utf-8"))\n\ndef sha(path):\n    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()\n\nclass TelemaqueS12CacheOnlyBindingTests(unittest.TestCase):\n    def test_exact_bounded_binding(self):\n        authority = load("series/odyssee/review/TELEMAQUE_FRENCH_CLEAN_PATH_V1.json")\n        self.assertEqual(authority["status"], "TELEMAQUE_FRENCH_CLEAN_PATH_HUMAN_PASS")\n        self.assertEqual(authority["human_result"]["audio_sha256"], "491ef48a0eed6f891f8226c7b4e6855fa4de3631ae9647794b6554852f0e7fae")\n        s12 = load("series/odyssee/programs/S12.json")\n        targets = {137, 147, 153}\n        routed = set()\n        for i, seg in enumerate(s12["segments"], start=1):\n            if seg.get("performance_provider") == "chatterbox-multilingual-v3":\n                routed.add(i)\n                self.assertEqual(seg.get("provider_seed"), 650100)\n                self.assertEqual(seg.get("character_id"), "telemaque")\n                self.assertEqual(seg.get("preset"), "odyssee-telemaque")\n            if seg.get("character_id") == "ulysse":\n                self.assertNotIn("performance_provider", seg)\n                self.assertNotIn("provider_seed", seg)\n        self.assertEqual(routed, targets)\n        package_path = "series/odyssee/production/provider-packages/TELEMAQUE_CHATTERBOX_FR_REFERENCE_V1.json"\n        self.assertEqual(sha(package_path), "918b0acc9eae83b2bce8722504180d1a2841321602e0d11aee5d9076c11154e8")\n        package = load(package_path)\n        self.assertEqual(package["synthesis"]["seed"], 650100)\n        self.assertEqual(package["synthesis"]["parameters"], {"language_id":"fr","reference":"p1-telemaque-human-pass","exaggeration":0.34,"cfg_weight":0.5,"temperature":0.74})\n        manifest = load("series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json")\n        unit = next(x for x in manifest["units"] if x["id"] == "S12")\n        self.assertEqual(unit["program_sha256"], sha("series/odyssee/programs/S12.json"))\n        self.assertEqual(unit["providers"], ["edge", "chatterbox-multilingual-v3"])\n        self.assertEqual(unit["provider_packages"][0]["package_sha256"], sha(package_path))\n\nif __name__ == "__main__":\n    unittest.main()\n'''
    TEST_PATH.write_text(test_source, encoding="utf-8")

    report = {
        "status": "TELEMAQUE_S12_PRODUCT_BINDING_MATERIALIZED_PENDING_CACHE_GATE",
        "program_sha256": program_sha,
        "voice_pack_sha256": voice_pack_sha,
        "provider_package_sha256": PACKAGE_SHA256,
        "reference_sha256": REFERENCE_SHA256,
        "targets": list(TARGETS),
    }
    write("generated/telemaque-s12/materialize.json", report)
    print(json.dumps(report, ensure_ascii=False))


def build_chatterbox_provider():
    from audio_engine.providers.factory import build_promoted_providers
    providers = build_promoted_providers(
        [PRODUCT_PACKAGE],
        workspace_root=".",
        model_cache_root="generated/provider-models",
    )
    return providers[PROVIDER]


def resolved_s12():
    from audio_engine.voices import load_voice_config, resolve_segments
    program = load(S12_PATH)
    voices, _ = load_voice_config(VOICE_PACK)
    return resolve_segments(program, voices)


def preseed():
    _, _, source_cache = verify_source_artifacts()
    provider = build_chatterbox_provider()
    from audio_engine.voice.render import voice_fingerprint
    resolved = resolved_s12()
    destination = Path("generated/work/S12/.cache/voices")
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for sequence, target in TARGETS.items():
        segment = resolved[sequence - 1]
        assert segment["provider"] == PROVIDER
        assert segment["performance_provider"] == PROVIDER
        assert int(segment["provider_seed"]) == FIXED_SEED
        expected_fingerprint = voice_fingerprint(segment, provider)
        source = source_cache / f"{target['source_fingerprint']}.mp3"
        assert sha(source) == target["clip_sha256"]
        dest = destination / f"{expected_fingerprint}.mp3"
        shutil.copyfile(source, dest)
        assert sha(dest) == target["clip_sha256"]
        dest.with_suffix(".json").unlink(missing_ok=True)
        records.append({
            "sequence": sequence,
            "source_fingerprint": target["source_fingerprint"],
            "production_fingerprint": expected_fingerprint,
            "clip_sha256": target["clip_sha256"],
            "byte_identity_preserved": True,
        })
    report = {
        "status": "TELEMAQUE_EXACT_ACCEPTED_CLIPS_PRESEEDED",
        "provider": PROVIDER,
        "provider_cache_identity": provider.cache_identity(),
        "records": records,
        "resynthesis": False,
        "audio_processing": False,
    }
    write("generated/telemaque-s12/preseed.json", report)
    print(json.dumps(report, ensure_ascii=False))


def fail_synthesize(*_args, **_kwargs):
    raise RuntimeError("CACHE_ONLY_GATE: provider synthesis/inference is forbidden")


def audit_all_voice_cache():
    from audio_engine.providers.edge import EdgeProvider
    from audio_engine.voice.render import render_voice_clip, voice_fingerprint
    chatterbox = build_chatterbox_provider()
    edge = EdgeProvider()
    # Neutralize both providers. Any true cache miss fails before the actual render.
    chatterbox.synthesize = fail_synthesize
    edge.synthesize = fail_synthesize
    providers = {PROVIDER: chatterbox, "edge": edge}
    cache_root = Path("generated/work/S12/.cache/voices")
    resolved = resolved_s12()
    records = []
    for sequence, segment in enumerate(resolved, start=1):
        provider = providers[segment["provider"]]
        expected = voice_fingerprint(segment, provider)
        path, hit, observed = render_voice_clip(segment, provider, cache_root)
        assert hit is True, sequence
        assert observed == expected, sequence
        assert path.is_file() and path.stat().st_size > 0, sequence
        records.append({"sequence": sequence, "provider": provider.name, "fingerprint": expected})
    report = {
        "status": "S12_ALL_VOICE_CACHE_FAIL_CLOSED_PASS",
        "segment_count": len(records),
        "cache_satisfied": len(records),
        "cache_misses": 0,
        "provider_inference_possible_during_audit": False,
        "records": records,
    }
    write("generated/telemaque-s12/all-voice-cache-audit.json", report)
    print(json.dumps({k: report[k] for k in report if k != "records"}, ensure_ascii=False))


def finalize():
    render_dir = Path("generated/work/S12/odyssee-s12")
    manifest_path = render_dir / "manifest.json"
    qa_path = render_dir / "qa-report.json"
    render_manifest = load(manifest_path)
    qa = load(qa_path)
    prewarm = load("generated/telemaque-s12/prewarm.json")
    preseed_report = load("generated/telemaque-s12/preseed.json")
    audit = load("generated/telemaque-s12/all-voice-cache-audit.json")
    assert prewarm["provider"] == PROVIDER
    assert prewarm["segment_count"] == 3
    assert prewarm["cache_hits"] == 3
    assert prewarm["cache_misses"] == 0
    assert audit["cache_misses"] == 0
    assert render_manifest["status"] == "success"
    assert render_manifest["mix"]["voice_cache_hits"] == render_manifest["mix"]["voice_clip_count"]
    assert qa["status"] == "PASS"

    audio_path = render_dir / render_manifest["audio"]["file"]
    s12_audio_sha = sha(audio_path)
    qa_sha = sha(qa_path)
    run_id = int(os.environ["GITHUB_RUN_ID"])
    head_before = os.environ.get("GITHUB_SHA")

    authority = load(AUTHORITY_PATH)
    integration = authority.setdefault("post_pass", {}).setdefault("integration", {})
    integration.update({
        "status": "TELEMAQUE_S12_CACHE_ONLY_MACHINE_QUALIFIED",
        "qualification_run": run_id,
        "qualification_head_before_commit": head_before,
        "prewarm": {"target": 3, "cache_hits": 3, "cache_misses": 0},
        "all_s12_voice_cache": {
            "segment_count": audit["segment_count"],
            "cache_satisfied": audit["cache_satisfied"],
            "cache_misses": 0,
        },
        "provider_inference": False,
        "resynthesis": False,
        "s12_machine_qa": "PASS",
        "s12_audio_sha256": s12_audio_sha,
        "s12_qa_sha256": qa_sha,
        "rollback": {
            "scope": "S12 segments 137/147/153 plus S12 manifest provider binding and this provider package only",
            "voice_pack_change": False,
            "ulysse_change": False,
            "global_telemaque_migration": False,
        },
    })
    write(AUTHORITY_PATH, authority)

    binding = {
        "schema": "recit.odyssee.telemaque_s12_cache_only_binding.v1",
        "status": "TELEMAQUE_S12_CACHE_ONLY_MACHINE_QUALIFIED",
        "authority_issue": 178,
        "human_verdict": "TELEMAQUE_FRENCH_CLEAN_PATH_HUMAN_PASS",
        "accepted_candidate": {
            "release": "odyssee-telemaque-fr-clean-level-recovery-v1",
            "audio_sha256": ACCEPTED_AUDIO_SHA256,
            "source_run": SOURCE_RUN,
            "source_artifact": SOURCE_ARTIFACT,
            "cache_artifact": CACHE_ARTIFACT,
            "recovery_run": RECOVERY_RUN,
        },
        "production_binding": {
            "scene": "S12",
            "segments": [137, 147, 153],
            "provider": PROVIDER,
            "provider_package": str(PRODUCT_PACKAGE),
            "provider_package_sha256": PACKAGE_SHA256,
            "reference_sha256": REFERENCE_SHA256,
            "seed": FIXED_SEED,
            "preseed_records": preseed_report["records"],
        },
        "machine_qualification": {
            "run": run_id,
            "prewarm": {"target": 3, "cache_hits": 3, "cache_misses": 0},
            "all_s12_voice_cache": {
                "segment_count": audit["segment_count"],
                "cache_satisfied": audit["cache_satisfied"],
                "cache_misses": 0,
            },
            "provider_inference": False,
            "resynthesis": False,
            "qa": "PASS",
            "s12_audio_sha256": s12_audio_sha,
            "qa_sha256": qa_sha,
        },
        "constraints": {
            "text_changed": False,
            "identity_preset_changed": False,
            "ulysse_changed": False,
            "s15_changed": False,
            "global_telemaque_migration": False,
            "provider_sweep": False,
        },
        "packaging": {
            "current_listening_release_github_immutable": False,
            "h2_immutable_production_release": "PENDING_BEFORE_H2_FAN_IN",
            "blocks_s12_machine_qualification": False,
            "blocks_h2_dispatch": True,
        },
    }
    write(BINDING_PATH, binding)
    report = {
        "status": "TELEMAQUE_S12_CACHE_ONLY_MACHINE_QUALIFIED",
        "run": run_id,
        "s12_audio_sha256": s12_audio_sha,
        "qa_sha256": qa_sha,
        "prewarm": binding["machine_qualification"]["prewarm"],
        "all_s12_voice_cache": binding["machine_qualification"]["all_s12_voice_cache"],
    }
    write("generated/telemaque-s12/final.json", report)
    print(json.dumps(report, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["materialize", "preseed", "audit-cache", "finalize"])
    args = parser.parse_args()
    if args.command == "materialize":
        materialize()
    elif args.command == "preseed":
        preseed()
    elif args.command == "audit-cache":
        audit_all_voice_cache()
    elif args.command == "finalize":
        finalize()


if __name__ == "__main__":
    main()
