#!/usr/bin/env python3
import argparse
import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import p6_s15_pipeline as intake
HUMAN_PROVIDER_PACKAGE = ROOT / "series/odyssee/production/provider-packages/P6_ULYSSES_HUMAN_BELTOUT_PRODUCTION_V1.json"
S15_PROGRAM = ROOT / "series/odyssee/programs/S15.json"
PRODUCTION_MANIFEST = ROOT / "series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json"
PRODUCTION_WORKFLOW = ROOT / ".github/workflows/odyssee-production.yml"

EXPECTED_SEGMENTS = intake.EXPECTED_SEGMENTS
ENGINE_REF = "f14a941d9218c2e9e632d7198557e7a3e48ff894"
ENGINE_VERSION = "0.9.2"
WINDOWS_RUNTIME_RUN = 33670957570
WINDOWS_RUNTIME_ARTIFACT = "beltout-portable-runtime-windows-x86_64"
WINDOWS_RUNTIME_ARTIFACT_DIGEST = "sha256:ea9f387016a4452b9918a980214e26a2bcb513a31ad561cc91d0f8dc9072bcc1"
ANCHOR_RUN = 33603995656
ANCHOR_ARTIFACT = "local-tts-p6-beltout-r0"
ANCHOR_SHA256 = "dc6266a224a3de4236c0eca8cbfb2364e97b16f558f514da48616451a3acad45"
RELEASE_TAG = "odyssee-p6-s15-ulysses-converted-v1"
RELEASE_ASSET = "p6-s15-ulysses-converted-v1.tar.xz"
PUBLIC_PROVIDER_PACKAGE = "series/odyssee/production/provider-packages/P6_ULYSSES_IMMUTABLE_CLIPS_V1.json"

CHECKPOINT_ROLES = {
    "decoder": "cfm_step_117580.safetensors",
    "pitch": "pitchmvmt_step_117580.safetensors",
    "encoder": "encoder_step_0.safetensors",
    "flow": "flow_step_0.safetensors",
    "mel2wav": "mel2wav_step_0.safetensors",
    "speaker": "speaker_encoder_step_0.safetensors",
    "tokenizer": "tokenizer_step_0.safetensors",
}


class P6PostCaptureError(ValueError):
    pass


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _provider_authority():
    package = load_json(HUMAN_PROVIDER_PACKAGE)
    if package.get("model", {}).get("revision") != "f71295e33cc9c0092083089ed0f9c1a532e77e6b":
        raise P6PostCaptureError("BeltOut authority revision drift")
    if package.get("target_identity", {}).get("derived_anchor_sha256") != ANCHOR_SHA256:
        raise P6PostCaptureError("Henri/Ulysse anchor authority drift")
    checkpoints = {
        item["file"]: item["sha256"]
        for item in package.get("model", {}).get("checkpoints", [])
    }
    if set(checkpoints) != set(CHECKPOINT_ROLES.values()):
        raise P6PostCaptureError("BeltOut checkpoint authority set drift")
    return package, checkpoints


def _checkpoint_manifest(package):
    by_name = {
        item["file"]: item["sha256"]
        for item in package["model"]["checkpoints"]
    }
    return {
        role: {"file": filename, "sha256": by_name[filename]}
        for role, filename in CHECKPOINT_ROLES.items()
    }


def _find_runtime_manifest(runtime_root):
    matches = list(Path(runtime_root).resolve().rglob("runtime-manifest.json"))
    valid = []
    for path in matches:
        try:
            data = load_json(path)
        except Exception:
            continue
        if data.get("schema") == "beltout-portable-runtime-v1":
            valid.append((path, data))
    if len(valid) != 1:
        raise P6PostCaptureError(
            f"expected exactly one BeltOut runtime manifest, found {len(valid)}"
        )
    return valid[0]


def resolve_runtime(runtime_root):
    package, checkpoints = _provider_authority()
    manifest_path, manifest = _find_runtime_manifest(runtime_root)
    portable = manifest_path.parent.resolve()

    if manifest.get("platform") != "windows-x86_64":
        raise P6PostCaptureError("P6 local runtime must be qualified Windows x86_64")
    if manifest.get("audio_engine_ref") != ENGINE_REF:
        raise P6PostCaptureError(
            f"Audio Engine runtime drift: {manifest.get('audio_engine_ref')} != {ENGINE_REF}"
        )
    if manifest.get("beltout_revision") != package["model"]["revision"]:
        raise P6PostCaptureError("BeltOut runtime revision drift")
    if manifest.get("contains_human_audio") is not False:
        raise P6PostCaptureError("portable runtime unexpectedly contains human audio")

    reported = {
        item["file"]: item["sha256"]
        for item in manifest.get("checkpoints", [])
    }
    if reported != checkpoints:
        raise P6PostCaptureError("portable runtime checkpoint manifest drift")

    checkpoint_dir = portable / "checkpoints"
    for filename, digest in checkpoints.items():
        target = checkpoint_dir / filename
        if not target.is_file():
            raise P6PostCaptureError(f"runtime checkpoint missing: {filename}")
        if sha256_file(target) != digest:
            raise P6PostCaptureError(f"runtime checkpoint SHA-256 drift: {filename}")

    python_path_file = portable / "python-path.txt"
    if not python_path_file.is_file():
        raise P6PostCaptureError("portable runtime python-path.txt missing")
    python_rel = python_path_file.read_text(encoding="ascii").strip()
    python_path = (portable / python_rel).resolve()
    try:
        python_path.relative_to(portable)
    except ValueError as exc:
        raise P6PostCaptureError("portable Python path escapes runtime root") from exc
    if not python_path.is_file():
        raise P6PostCaptureError("portable Python executable missing")

    beltout_source = portable / "beltout-src"
    if not beltout_source.is_dir():
        raise P6PostCaptureError("portable BeltOut source missing")

    return {
        "root": portable,
        "python": python_path,
        "beltout_source": beltout_source,
        "checkpoint_dir": checkpoint_dir,
        "manifest": manifest,
    }


def resolve_anchor(anchor_root):
    root = Path(anchor_root).resolve()
    if not root.exists():
        raise P6PostCaptureError(f"anchor artifact root not found: {root}")
    matches = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() == ".wav":
            try:
                digest = sha256_file(path)
            except OSError:
                continue
            if digest == ANCHOR_SHA256:
                matches.append(path.resolve())
    if len(matches) != 1:
        raise P6PostCaptureError(
            f"expected exactly one exact Henri/Ulysse anchor, found {len(matches)}"
        )
    return matches[0]


def _write_once_json(path, data):
    path = Path(path)
    if path.exists():
        existing = load_json(path)
        if existing != data:
            raise P6PostCaptureError(f"immutable local metadata drift: {path}")
        return
    write_json(path, data)


def _validate_report(report_path, output_path, slot, package):
    report = load_json(report_path)
    if report.get("status") != "PASS":
        raise P6PostCaptureError(
            f"segment {slot['segment']} BeltOut report is not PASS"
        )
    if report.get("retry_allowed_after_output") is not False:
        raise P6PostCaptureError("BeltOut retry prohibition drift")
    if report.get("network_used") is not False:
        raise P6PostCaptureError("BeltOut conversion unexpectedly used network")
    inputs = report.get("inputs") or {}
    if inputs.get("source_sha256") != slot["source_sha256"]:
        raise P6PostCaptureError(
            f"segment {slot['segment']} report source authority mismatch"
        )
    if inputs.get("target_reference_sha256") != ANCHOR_SHA256:
        raise P6PostCaptureError("BeltOut target anchor mismatch")
    if inputs.get("beltout_revision") != package["model"]["revision"]:
        raise P6PostCaptureError("BeltOut revision mismatch in conversion report")
    conversion = report.get("conversion") or {}
    if conversion.get("seed") != slot["seed"]:
        raise P6PostCaptureError(f"segment {slot['segment']} seed mismatch")
    if conversion.get("n_timesteps") != 10:
        raise P6PostCaptureError(f"segment {slot['segment']} timestep mismatch")
    for flag in ("best_of_n", "second_pass", "time_stretch", "pitch_shift", "emotion_dsp"):
        if conversion.get(flag) is not False:
            raise P6PostCaptureError(
                f"segment {slot['segment']} forbidden conversion flag: {flag}"
            )
    evidence = report.get("evidence") or {}
    if evidence.get("pass") is not True:
        raise P6PostCaptureError(f"segment {slot['segment']} machine evidence failed")
    decode = evidence.get("audio_decode") or {}
    if decode.get("persistent_normalized_raw_file") is not False:
        raise P6PostCaptureError(
            f"segment {slot['segment']} persistent normalized raw file forbidden"
        )
    if decode.get("filters") not in ([], None):
        raise P6PostCaptureError(f"segment {slot['segment']} decode filters forbidden")

    output = report.get("output") or {}
    if not Path(output_path).is_file():
        raise P6PostCaptureError(f"segment {slot['segment']} converted output missing")
    actual_output_sha = sha256_file(output_path)
    if output.get("sha256") != actual_output_sha:
        raise P6PostCaptureError(
            f"segment {slot['segment']} converted output hash mismatch"
        )
    return report, actual_output_sha


def convert(frozen_path, runtime_root, anchor_root):
    frozen_path = Path(frozen_path).resolve()
    private_root = frozen_path.parent.resolve()
    intake.require_private_output(private_root)
    frozen = intake.verify_frozen(frozen_path)
    if tuple(frozen.get("segments") or []) != EXPECTED_SEGMENTS:
        raise P6PostCaptureError("frozen intake does not match exact S15 scope")

    package, _ = _provider_authority()
    runtime = resolve_runtime(runtime_root)
    anchor = resolve_anchor(anchor_root)

    checkpoint_manifest = _checkpoint_manifest(package)
    checkpoint_manifest_path = private_root / "beltout-checkpoints.json"
    _write_once_json(checkpoint_manifest_path, checkpoint_manifest)

    converted_dir = private_root / "converted"
    reports_dir = private_root / "conversion-reports"
    logs_dir = private_root / "conversion-logs"
    converted_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for slot in frozen.get("slots") or []:
        segment = int(slot["segment"])
        if segment not in EXPECTED_SEGMENTS:
            raise P6PostCaptureError(f"unexpected frozen segment: {segment}")
        source = Path(slot["private_source_path"]).resolve()
        output = converted_dir / f"p6-s15-{segment}-ulysse.wav"
        report_path = reports_dir / f"p6-s15-{segment}.json"
        log_path = logs_dir / f"p6-s15-{segment}.log"

        if output.exists() or report_path.exists():
            if not output.is_file() or not report_path.is_file():
                raise P6PostCaptureError(
                    f"segment {segment} has partial prior one-shot output; retry forbidden"
                )
            _, output_sha = _validate_report(report_path, output, slot, package)
            results.append({
                "segment": segment,
                "state": "RESUMED_VERIFIED_NO_RECONVERSION",
                "output_path": str(output),
                "output_sha256": output_sha,
                "report_path": str(report_path),
            })
            continue

        command = [
            str(runtime["python"]),
            "-m",
            "audio_engine.cli",
            "voice-conversion",
            "beltout-once",
            "--source",
            str(source),
            "--source-sha256",
            slot["source_sha256"],
            "--target-reference",
            str(anchor),
            "--target-reference-sha256",
            ANCHOR_SHA256,
            "--beltout-source",
            str(runtime["beltout_source"]),
            "--expected-revision",
            package["model"]["revision"],
            "--checkpoint-dir",
            str(runtime["checkpoint_dir"]),
            "--checkpoint-manifest",
            str(checkpoint_manifest_path),
            "--seed",
            str(slot["seed"]),
            "--n-timesteps",
            "10",
            "--out",
            str(output),
            "--report",
            str(report_path),
        ]
        process = subprocess.run(
            command,
            cwd=runtime["root"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_path.write_text(process.stdout or "", encoding="utf-8")
        if process.returncode != 0:
            raise P6PostCaptureError(
                f"segment {segment} one-shot BeltOut conversion failed; "
                f"no retry is authorized after any output appears; inspect {log_path}"
            )
        _, output_sha = _validate_report(report_path, output, slot, package)
        results.append({
            "segment": segment,
            "state": "CONVERTED_EXACTLY_ONCE",
            "output_path": str(output),
            "output_sha256": output_sha,
            "report_path": str(report_path),
        })

    if tuple(item["segment"] for item in results) != EXPECTED_SEGMENTS:
        raise P6PostCaptureError("conversion result set is not exact 12/12")

    conversion_set = {
        "schema": "recit.odyssee.p6.s15.private_conversion_set.v1",
        "status": "P6_S15_12_OF_12_BELTOUT_MACHINE_PASS",
        "segments": list(EXPECTED_SEGMENTS),
        "engine_ref": ENGINE_REF,
        "runtime_run": WINDOWS_RUNTIME_RUN,
        "runtime_artifact": WINDOWS_RUNTIME_ARTIFACT,
        "runtime_artifact_digest": WINDOWS_RUNTIME_ARTIFACT_DIGEST,
        "anchor_sha256": ANCHOR_SHA256,
        "beltout_revision": package["model"]["revision"],
        "n_timesteps": 10,
        "raw_human_voice_publication": "FORBIDDEN",
        "results": results,
    }
    write_json(private_root / "conversion-set.json", conversion_set)
    return conversion_set


def _tar_add_bytes(archive, name, data):
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def _publishable_index(conversion_set):
    clips = []
    for item in conversion_set["results"]:
        output = Path(item["output_path"])
        digest = sha256_file(output)
        if digest != item["output_sha256"]:
            raise P6PostCaptureError(
                f"converted output drift for segment {item['segment']}"
            )
        clips.append({
            "segment": item["segment"],
            "id": f"p6-s15-{item['segment']}",
            "file": output.name,
            "sha256": digest,
        })
    return {
        "schema": "recit.odyssee.p6.s15.converted_release.v1",
        "status": "PUBLISHABLE_CONVERTED_ONLY_12_OF_12",
        "segments": list(EXPECTED_SEGMENTS),
        "release_tag": RELEASE_TAG,
        "release_asset": RELEASE_ASSET,
        "engine_ref": ENGINE_REF,
        "beltout_revision": conversion_set["beltout_revision"],
        "anchor_sha256": ANCHOR_SHA256,
        "contains_raw_human_audio": False,
        "contains_private_source_paths": False,
        "clips": clips,
    }


def _build_archive(conversion_set, target):
    index = _publishable_index(conversion_set)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    with tarfile.open(target, mode="w:xz", format=tarfile.PAX_FORMAT) as archive:
        index_bytes = (
            json.dumps(index, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        _tar_add_bytes(archive, "p6-converted-index.json", index_bytes)
        for item in conversion_set["results"]:
            source = Path(item["output_path"])
            _tar_add_bytes(archive, f"clips/{source.name}", source.read_bytes())
    return index, sha256_file(target)


def _build_provider_package(index, archive_sha, manifest):
    s15_unit = next(
        (unit for unit in manifest["units"] if unit.get("id") == "S15"),
        None,
    )
    if not s15_unit:
        raise P6PostCaptureError("S15 Production unit missing")
    voice_pack_sha = s15_unit["voice_pack_sha256"]
    references = []
    integrity = []
    for clip in index["clips"]:
        workspace_path = (
            f"series/odyssee/production/provider-assets/p6/{clip['file']}"
        )
        source = {
            "type": "github_release_archive",
            "repository": "stefm78/recit-audioguide",
            "tag": RELEASE_TAG,
            "asset": RELEASE_ASSET,
            "asset_sha256": archive_sha,
            "member_basename": clip["file"],
        }
        references.append({
            "id": clip["id"],
            "path": workspace_path,
            "sha256": clip["sha256"],
            "source": source,
        })
        integrity.append({
            "name": clip["file"],
            "path": workspace_path,
            "sha256": clip["sha256"],
        })

    return {
        "schema_version": 1,
        "id": "odyssee-p6-ulysse-immutable-clips-v1",
        "provider": {
            "id": "immutable-voice-clips-v1",
            "implementation_version": "1.0.0",
        },
        "runtime": {
            "kind": "python",
            "python": "3.12",
            "device": "cpu",
            "dependencies": [
                {"name": "recit-audio-engine", "version": ENGINE_VERSION}
            ],
        },
        "model": {
            "id": "odyssee-p6-s15-ulysses-converted-clips",
            "source": "local",
            "revision": RELEASE_TAG,
            "integrity": integrity,
        },
        "voice_pack_sha256": voice_pack_sha,
        "synthesis": {"seed": 0, "parameters": {}},
        "references": references,
        "fallback": "fail",
    }


def _staged_s15(index):
    program = load_json(S15_PROGRAM)
    by_segment = {item["segment"]: item for item in index["clips"]}
    for segment in EXPECTED_SEGMENTS:
        current = program["segments"][segment - 1]
        if current.get("speaker") != "ULYSSE":
            raise P6PostCaptureError(f"S15 segment {segment} is no longer ULYSSE")
        if current.get("performance_provider") is not None:
            raise P6PostCaptureError(
                f"S15 segment {segment} already has a performance provider"
            )
        current["performance_provider"] = "immutable-voice-clips-v1"
        current["provider_parameters"] = {
            "reference": by_segment[segment]["id"]
        }

    production = program["production"]
    production["state"] = "READY"
    production["blockers"] = []
    penelope = production.get("p6_penelope") or {}
    penelope.pop("remaining_hold", None)
    ulysses = production.get("p6_ulysse") or {}
    ulysses["state"] = "MATERIALIZED_BELTOUT_IMMUTABLE_CLIPS"
    ulysses["performance_provider"] = "immutable-voice-clips-v1"
    ulysses["provider_package"] = PUBLIC_PROVIDER_PACKAGE
    ulysses["immutable_release_tag"] = RELEASE_TAG
    ulysses["immutable_release_asset"] = RELEASE_ASSET
    ulysses["raw_human_audio_policy"] = "NEVER_COMMIT_TO_PUBLIC_REPOSITORY"
    ulysses["source_publication"] = "CONVERTED_OUTPUTS_ONLY"
    return program


def _staged_manifest(program_sha, provider_sha):
    manifest = load_json(PRODUCTION_MANIFEST)
    old_engine = manifest.get("engine_ref")
    manifest["engine_ref"] = ENGINE_REF
    policy = manifest.get("policy") or {}
    workflow = policy.get("production_workflow")
    if isinstance(workflow, str) and old_engine and old_engine in workflow:
        policy["production_workflow"] = workflow.replace(old_engine, ENGINE_REF)

    unit = next(
        (item for item in manifest["units"] if item.get("id") == "S15"),
        None,
    )
    if not unit:
        raise P6PostCaptureError("S15 Production unit missing")
    unit["state"] = "ready"
    unit["program_sha256"] = program_sha
    unit.pop("hold_reason", None)

    packages = [
        item
        for item in unit.get("provider_packages", [])
        if item.get("provider") != "immutable-voice-clips-v1"
    ]
    packages.append({
        "provider": "immutable-voice-clips-v1",
        "package": PUBLIC_PROVIDER_PACKAGE,
        "package_sha256": provider_sha,
    })
    unit["provider_packages"] = packages

    providers = list(unit.get("providers") or [])
    if "immutable-voice-clips-v1" not in providers:
        providers.append("immutable-voice-clips-v1")
    unit["providers"] = providers
    unit["provider"] = "+".join(providers)
    return manifest


def _staged_workflow():
    text = PRODUCTION_WORKFLOW.read_text(encoding="utf-8")
    old = "uses: stefm78/audio-engine/.github/workflows/production.yml@"
    lines = []
    replaced = 0
    for line in text.splitlines():
        if old in line:
            prefix = line.split(old, 1)[0]
            line = prefix + old + ENGINE_REF
            replaced += 1
        if "fresh_scene_cache_units_json:" in line:
            indentation = line[: len(line) - len(line.lstrip())]
            line = (
                indentation
                + "fresh_scene_cache_units_json: '[\"S09\",\"S15\"]'"
            )
        lines.append(line)
    if replaced != 1:
        raise P6PostCaptureError("Production workflow engine pin shape drift")
    return "\n".join(lines) + "\n"


def _assert_no_private_leak(staging_root, conversion_set):
    forbidden = set()
    for item in conversion_set["results"]:
        forbidden.add(str(Path(item["output_path"]).parent))
        report_parent = str(Path(item["report_path"]).parent)
        forbidden.add(report_parent)
    for path in Path(staging_root).rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".wav", ".xz"}:
            continue
        text = path.read_text(encoding="utf-8")
        for needle in forbidden:
            if needle and needle in text:
                raise P6PostCaptureError(
                    f"private local path leaked into staged artifact: {path}"
                )
        if "private_source_path" in text:
            raise P6PostCaptureError(
                f"raw human private path key leaked into staged artifact: {path}"
            )


def stage(conversion_set_path, out_dir):
    conversion_set_path = Path(conversion_set_path).resolve()
    private_root = conversion_set_path.parent.resolve()
    intake.require_private_output(private_root)
    conversion_set = load_json(conversion_set_path)
    if conversion_set.get("status") != "P6_S15_12_OF_12_BELTOUT_MACHINE_PASS":
        raise P6PostCaptureError("conversion set is not machine PASS")
    if tuple(conversion_set.get("segments") or []) != EXPECTED_SEGMENTS:
        raise P6PostCaptureError("conversion set segment scope drift")
    if len(conversion_set.get("results") or []) != 12:
        raise P6PostCaptureError("conversion set must contain exactly 12 results")

    out_dir = Path(out_dir).resolve()
    intake.require_private_output(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    publishable = out_dir / "publishable"
    staged = out_dir / "staged-product"
    publishable.mkdir(parents=True)
    staged.mkdir(parents=True)

    archive_path = publishable / RELEASE_ASSET
    index, archive_sha = _build_archive(conversion_set, archive_path)
    index["release_asset_sha256"] = archive_sha
    write_json(publishable / "p6-converted-index.json", index)

    manifest_authority = load_json(PRODUCTION_MANIFEST)
    provider_package = _build_provider_package(index, archive_sha, manifest_authority)
    provider_path = staged / PUBLIC_PROVIDER_PACKAGE
    write_json(provider_path, provider_package)
    provider_sha = sha256_file(provider_path)

    staged_program = _staged_s15(index)
    program_path = staged / "series/odyssee/programs/S15.json"
    write_json(program_path, staged_program)
    program_sha = sha256_file(program_path)

    staged_manifest = _staged_manifest(program_sha, provider_sha)
    manifest_path = staged / "series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json"
    write_json(manifest_path, staged_manifest)

    workflow_path = staged / ".github/workflows/odyssee-production.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(_staged_workflow(), encoding="utf-8")

    apply_order = {
        "schema": "recit.odyssee.p6.s15.materialization_apply_order.v1",
        "status": "READY_AFTER_CONVERTED_RELEASE_PUBLICATION",
        "release": {
            "tag": RELEASE_TAG,
            "asset": RELEASE_ASSET,
            "asset_sha256": archive_sha,
            "contains_raw_human_audio": False,
        },
        "apply_after_release_only": [
            PUBLIC_PROVIDER_PACKAGE,
            "series/odyssee/programs/S15.json",
            "series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json",
            ".github/workflows/odyssee-production.yml",
        ],
        "engine_ref": ENGINE_REF,
        "force_fresh_units": ["S09", "S15"],
        "raw_human_audio_repository_policy": "FORBIDDEN",
        "h2_dispatch": "FORBIDDEN_WHILE_P7_OPEN",
    }
    write_json(out_dir / "APPLY_ORDER.json", apply_order)
    _assert_no_private_leak(out_dir, conversion_set)

    result = {
        "schema": "recit.odyssee.p6.s15.post_capture_stage.v1",
        "status": "P6_S15_POST_CAPTURE_STAGE_READY",
        "publishable_archive": str(archive_path),
        "publishable_archive_sha256": archive_sha,
        "publishable_index": str(publishable / "p6-converted-index.json"),
        "staged_product_root": str(staged),
        "provider_package_sha256": provider_sha,
        "staged_program_sha256": program_sha,
        "release_tag": RELEASE_TAG,
        "release_asset": RELEASE_ASSET,
        "contains_raw_human_audio": False,
        "contains_private_source_paths": False,
    }
    write_json(out_dir / "stage-result.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="P6 S15 private one-shot conversion and converted-only staging"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    convert_cmd = sub.add_parser("convert")
    convert_cmd.add_argument("--frozen", required=True)
    convert_cmd.add_argument("--runtime-root", required=True)
    convert_cmd.add_argument("--anchor-root", required=True)

    stage_cmd = sub.add_parser("stage")
    stage_cmd.add_argument("--conversion-set", required=True)
    stage_cmd.add_argument("--out", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "convert":
            result = convert(args.frozen, args.runtime_root, args.anchor_root)
        else:
            result = stage(args.conversion_set, args.out)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (
        P6PostCaptureError,
        intake.P6IntakeError,
        OSError,
        json.JSONDecodeError,
        tarfile.TarError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
