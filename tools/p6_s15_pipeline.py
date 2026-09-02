#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_CONTRACT = ROOT / "series/odyssee/production/P6_S15_PRODUCTION_CAPTURE_V1.json"
PROGRAM = ROOT / "series/odyssee/programs/S15.json"
PROVIDER_PACKAGE = ROOT / "series/odyssee/production/provider-packages/P6_ULYSSES_HUMAN_BELTOUT_PRODUCTION_V1.json"
EXPECTED_SEGMENTS = (112, 114, 116, 118, 120, 133, 135, 140, 142, 151, 153, 158)
CAPTURE_SCHEMA = "odyssee-p6-s15-production-human-capture-v1"
CAPTURE_STATUS = "FROZEN_SELECTED_TAKES_READY_FOR_SINGLE_BELTOUT_CONVERSION"
RAW_POLICY = "NEVER_COMMIT_TO_PUBLIC_REPOSITORY"
ALLOWED_EXTENSIONS = {".wav", ".webm", ".ogg", ".m4a", ".mp4"}


class P6IntakeError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_inside(path: Path, root: Path) -> bool:
    path = path.resolve()
    root = root.resolve()
    return path == root or root in path.parents


def require_private_output(path: Path):
    path = path.resolve()
    if is_inside(path, ROOT):
        raise P6IntakeError(
            "raw human audio private workspace must be outside the public repository checkout"
        )


def parse_sums(text: str):
    result = {}
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise P6IntakeError(f"SHA256SUMS.txt line {lineno} is invalid")
        digest, name = match.groups()
        if name in result:
            raise P6IntakeError(f"duplicate SHA256SUMS entry: {name}")
        result[name] = digest
    return result


def safe_zip_names(zf: zipfile.ZipFile):
    names = zf.namelist()
    if len(names) != len(set(names)):
        raise P6IntakeError("ZIP contains duplicate filenames")
    for name in names:
        p = Path(name)
        if p.is_absolute() or ".." in p.parts or name.endswith("/"):
            raise P6IntakeError(f"unsafe or directory ZIP member: {name}")
    return names


def exact_target_map():
    contract = load_json(CAPTURE_CONTRACT)
    targets = contract.get("targets") or []
    by_segment = {int(item["segment"]): item for item in targets}
    if tuple(by_segment) != EXPECTED_SEGMENTS:
        raise P6IntakeError("repository capture contract does not match exact 12 S15 segments")
    return contract, by_segment


def validate_authorities():
    contract, targets = exact_target_map()
    program = load_json(PROGRAM)
    for segment in EXPECTED_SEGMENTS:
        current = program["segments"][segment - 1]
        expected = targets[segment]
        if current.get("speaker") != "ULYSSE" or current.get("text") != expected.get("text"):
            raise P6IntakeError(f"S15 frozen speaker/text guard mismatch at segment {segment}")
    package = load_json(PROVIDER_PACKAGE)
    if package.get("provider", {}).get("id") != "human-performance-beltout":
        raise P6IntakeError("unexpected P6 BeltOut provider id")
    if package.get("model", {}).get("revision") != "f71295e33cc9c0092083089ed0f9c1a532e77e6b":
        raise P6IntakeError("unexpected BeltOut model revision")
    if package.get("synthesis", {}).get("parameters", {}).get("n_timesteps") != 10:
        raise P6IntakeError("P6 BeltOut n_timesteps must remain 10")
    if package.get("synthesis", {}).get("post_conversion", {}).get("allowed") != [
        "constant_level_alignment_only"
    ]:
        raise P6IntakeError("P6 post-conversion policy drift")
    return contract, targets, package


def validate_capture_manifest(manifest, targets):
    if manifest.get("schema") != CAPTURE_SCHEMA:
        raise P6IntakeError(f"capture schema mismatch: {manifest.get('schema')}")
    if manifest.get("status") != CAPTURE_STATUS:
        raise P6IntakeError(f"capture status mismatch: {manifest.get('status')}")
    if manifest.get("segment_count") != 12:
        raise P6IntakeError("capture segment_count must be exactly 12")
    if tuple(manifest.get("segments") or []) != EXPECTED_SEGMENTS:
        raise P6IntakeError("capture segment list must match exact frozen S15 scope")
    if manifest.get("raw_human_voice_repository_policy") != RAW_POLICY:
        raise P6IntakeError("raw human voice repository policy mismatch")
    post = manifest.get("post_freeze") or {}
    if post.get("conversion") != "EXACTLY_ONE_BELTOUT_CONVERSION_PER_SELECTED_TAKE":
        raise P6IntakeError("post-freeze conversion rule mismatch")
    if post.get("best_of_n") is not False or post.get("second_pass") is not False:
        raise P6IntakeError("best-of-N and second BeltOut pass must remain forbidden")
    if post.get("post_conversion_processing") != ["constant_level_alignment_only"]:
        raise P6IntakeError("only constant level alignment is allowed after conversion")

    slots = manifest.get("slots") or []
    if len(slots) != 12:
        raise P6IntakeError("capture manifest must contain exactly 12 slots")
    by_segment = {}
    filenames = set()
    for slot in slots:
        try:
            segment = int(slot["segment"])
        except Exception as exc:
            raise P6IntakeError("capture slot segment is invalid") from exc
        if segment in by_segment:
            raise P6IntakeError(f"duplicate capture slot segment: {segment}")
        if segment not in EXPECTED_SEGMENTS:
            raise P6IntakeError(f"unexpected capture segment: {segment}")
        if slot.get("text") != targets[segment]["text"]:
            raise P6IntakeError(f"capture text mismatch at segment {segment}")
        if slot.get("selected_before_conversion") is not True:
            raise P6IntakeError(f"segment {segment} was not frozen before conversion")
        if slot.get("clean_capture_confirmed") is not True:
            raise P6IntakeError(f"segment {segment} clean capture was not confirmed")
        filename = slot.get("filename")
        if not isinstance(filename, str) or not filename:
            raise P6IntakeError(f"segment {segment} filename missing")
        if Path(filename).name != filename:
            raise P6IntakeError(f"segment {segment} filename must be a basename")
        if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
            raise P6IntakeError(f"segment {segment} unsupported capture extension")
        if filename in filenames:
            raise P6IntakeError(f"duplicate capture filename: {filename}")
        filenames.add(filename)
        digest = slot.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise P6IntakeError(f"segment {segment} SHA-256 is invalid")
        if not isinstance(slot.get("duration_seconds"), (int, float)) or not 0.20 <= float(slot["duration_seconds"]) <= 20.0:
            raise P6IntakeError(f"segment {segment} duration is outside capture bounds")
        by_segment[segment] = slot
    if tuple(sorted(by_segment)) != EXPECTED_SEGMENTS:
        raise P6IntakeError("capture slots do not cover exact 12 frozen S15 segments")
    return by_segment


def intake(zip_path: Path, private_out: Path):
    zip_path = Path(zip_path).resolve()
    private_out = Path(private_out).resolve()
    require_private_output(private_out)
    if not zip_path.is_file():
        raise P6IntakeError(f"capture ZIP not found: {zip_path}")

    contract, targets, package = validate_authorities()
    zip_digest = sha256_file(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = safe_zip_names(zf)
        required_meta = {"recording-manifest.json", "SHA256SUMS.txt", "README.txt"}
        if not required_meta.issubset(names):
            raise P6IntakeError("capture ZIP is missing required metadata files")

        manifest_bytes = zf.read("recording-manifest.json")
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except Exception as exc:
            raise P6IntakeError(f"recording-manifest.json is invalid: {exc}") from exc
        slots = validate_capture_manifest(manifest, targets)

        sums = parse_sums(zf.read("SHA256SUMS.txt").decode("utf-8"))
        manifest_sha = sha256_bytes(manifest_bytes)
        if sums.get("recording-manifest.json") != manifest_sha:
            raise P6IntakeError("recording-manifest.json SHA-256 mismatch")

        expected_audio_names = {slot["filename"] for slot in slots.values()}
        actual_audio_names = {
            name for name in names if Path(name).suffix.lower() in ALLOWED_EXTENSIONS
        }
        if actual_audio_names != expected_audio_names:
            raise P6IntakeError(
                f"ZIP audio member set mismatch: {sorted(actual_audio_names)} != {sorted(expected_audio_names)}"
            )
        unexpected = set(names) - required_meta - expected_audio_names
        if unexpected:
            raise P6IntakeError(f"ZIP contains unexpected members: {sorted(unexpected)}")

        raw_dir = private_out / "raw-selected"
        if private_out.exists():
            shutil.rmtree(private_out)
        raw_dir.mkdir(parents=True, exist_ok=True)

        frozen_slots = []
        for segment in EXPECTED_SEGMENTS:
            slot = slots[segment]
            data = zf.read(slot["filename"])
            actual_sha = sha256_bytes(data)
            if actual_sha != slot["sha256"]:
                raise P6IntakeError(f"segment {segment} audio SHA-256 mismatch vs manifest")
            if sums.get(slot["filename"]) != actual_sha:
                raise P6IntakeError(f"segment {segment} audio SHA-256 mismatch vs SHA256SUMS")
            target = raw_dir / slot["filename"]
            target.write_bytes(data)
            frozen_slots.append({
                "segment": segment,
                "text": targets[segment]["text"],
                "group": targets[segment]["group"],
                "source_filename": slot["filename"],
                "private_source_path": str(target),
                "source_sha256": actual_sha,
                "duration_seconds": float(slot["duration_seconds"]),
                "seed": 202609060000 + segment,
                "conversion_count_required": 1,
            })

    freeze_core = {
        "schema": "recit.odyssee.p6.s15.frozen_intake.v1",
        "status": "FROZEN_12_OF_12_READY_FOR_SINGLE_BELTOUT_CONVERSION",
        "capture_contract": str(CAPTURE_CONTRACT.relative_to(ROOT)),
        "provider_package": str(PROVIDER_PACKAGE.relative_to(ROOT)),
        "provider_package_sha256": sha256_file(PROVIDER_PACKAGE),
        "zip_sha256": zip_digest,
        "recording_manifest_sha256": manifest_sha,
        "segments": list(EXPECTED_SEGMENTS),
        "raw_human_voice_repository_policy": RAW_POLICY,
        "conversion_policy": {
            "beltout_revision": package["model"]["revision"],
            "n_timesteps": 10,
            "exactly_one_conversion_per_selected_take": True,
            "best_of_n": False,
            "second_pass": False,
            "post_conversion_processing": ["constant_level_alignment_only"],
        },
        "slots": frozen_slots,
    }
    freeze_digest = hashlib.sha256(
        json.dumps(freeze_core, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    freeze_core["freeze_sha256"] = freeze_digest
    write_json(private_out / "frozen-intake.json", freeze_core)
    (private_out / "FREEZE.lock").write_text(freeze_digest + "\n", encoding="ascii")

    plan = {
        "schema": "recit.odyssee.p6.s15.beltout_conversion_plan.v1",
        "status": "READY_FOR_EXACTLY_ONE_CONVERSION_PER_FROZEN_TAKE",
        "frozen_intake": str(private_out / "frozen-intake.json"),
        "freeze_sha256": freeze_digest,
        "provider_package": str(PROVIDER_PACKAGE),
        "beltout_revision": package["model"]["revision"],
        "target_identity": package["target_identity"],
        "n_timesteps": 10,
        "slots": [
            {
                "segment": slot["segment"],
                "source_sha256": slot["source_sha256"],
                "seed": slot["seed"],
                "conversion_ordinal": 1,
                "allow_retry_after_audio_output_exists": False,
                "post_conversion_processing": ["constant_level_alignment_only"],
            }
            for slot in frozen_slots
        ],
        "composition": {
            "program": str(PROGRAM),
            "preserve_penelope_materialization": True,
            "replace_only_segments": list(EXPECTED_SEGMENTS),
            "automatic_qa_required": True,
            "block_d_qa_required": True,
        },
    }
    write_json(private_out / "conversion-plan.json", plan)
    return freeze_core, plan


def verify_frozen(frozen_path: Path):
    frozen_path = Path(frozen_path).resolve()
    frozen = load_json(frozen_path)
    if frozen.get("segments") != list(EXPECTED_SEGMENTS):
        raise P6IntakeError("frozen intake segment set drift")
    expected_freeze = frozen.get("freeze_sha256")
    core = dict(frozen)
    core.pop("freeze_sha256", None)
    actual_freeze = hashlib.sha256(
        json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if actual_freeze != expected_freeze:
        raise P6IntakeError("frozen intake digest mismatch")
    for slot in frozen.get("slots") or []:
        path = Path(slot["private_source_path"])
        if not path.is_file():
            raise P6IntakeError(f"frozen source missing for segment {slot['segment']}")
        if sha256_file(path) != slot["source_sha256"]:
            raise P6IntakeError(f"frozen source hash drift for segment {slot['segment']}")
    return frozen


def main(argv=None):
    parser = argparse.ArgumentParser(description="P6 S15 private human-capture intake and freeze gate")
    sub = parser.add_subparsers(dest="command", required=True)

    intake_cmd = sub.add_parser("intake")
    intake_cmd.add_argument("zip")
    intake_cmd.add_argument("--private-out", required=True)

    verify_cmd = sub.add_parser("verify-frozen")
    verify_cmd.add_argument("frozen_intake")

    args = parser.parse_args(argv)
    try:
        if args.command == "intake":
            frozen, plan = intake(Path(args.zip), Path(args.private_out))
            result = {
                "status": frozen["status"],
                "segment_count": len(frozen["slots"]),
                "freeze_sha256": frozen["freeze_sha256"],
                "conversion_plan": plan["status"],
                "private_workspace": str(Path(args.private_out).resolve()),
            }
        else:
            frozen = verify_frozen(Path(args.frozen_intake))
            result = {
                "status": "FROZEN_INTAKE_VERIFIED",
                "segment_count": len(frozen["slots"]),
                "freeze_sha256": frozen["freeze_sha256"],
            }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (P6IntakeError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
