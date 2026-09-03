#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

try:
    from tools import p7_round2_render as r2
except ModuleNotFoundError:
    import p7_round2_render as r2

ROOT = r2.ROOT
CONTRACT = r2.CONTRACT
MANIFEST = r2.MANIFEST
ENGINE_REF = "1ea5c052d2212875c1f8290bc179908265387cf8"
ROUND2_RELEASE_TAG = "odyssee-p7-round2-line-microprosody-v1"
ROUND2_FATHER_ASSET = "p7-r2-father-c.mp3"
ROUND2_FATHER_SHA256 = "cb72b83a5df08f4a8af958e0ddd6fc6b3af797253d08013a20c0101d6cd8484d"
REPAIR_RELEASE_TAG = "odyssee-p7-r2-father-context-repair-v1"
REPAIR_AUDIO = "p7-r2-father-context-repair.mp3"
REPAIR_QA = "p7-r2-father-context-repair.qa-report.json"
REPAIR_INDEX = "p7-r2-father-context-repair-index.json"
FATHER_ID = "father"
TELEMAQUE_SEGMENTS = (137, 139, 143, 145, 147, 149, 151, 153)
EXPECTED_TELEMAQUE_PRESET = {
    "voice": "fr-FR-RemyMultilingualNeural",
    "rate": "+5%",
    "pitch": "+8Hz",
    "volume": "+2%",
    "provider": "edge",
}


class RepairError(ValueError):
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


def digest_json(value):
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def father_window(contract):
    if contract.get("status") != r2.EXPECTED_STATUS:
        raise RepairError("Round 2 authority status drift")
    matches = [
        item for item in contract.get("windows") or []
        if item.get("id") == FATHER_ID
    ]
    if len(matches) != 1:
        raise RepairError("expected exactly one father Round 2 window")
    return matches[0]


def _preset_map(voice_pack):
    return r2.base._preset_map(voice_pack)


def _absolute_segments(program, start):
    return {
        start + offset: segment
        for offset, segment in enumerate(program.get("segments") or [])
    }


def _ulysse_snapshot(program, voice_pack, window):
    presets = _preset_map(voice_pack)
    ulysse = presets["odyssee-ulysse"]
    start = int(window["range"]["start_segment"])
    by_abs = _absolute_segments(program, start)
    result = []
    for number in window["ulysse_segments"]:
        segment = by_abs[number]
        override = window["C"]["segment_overrides"][str(number)]
        expected = {
            "segment": number,
            "speaker": "ULYSSE",
            "text": next(
                guard["text"]
                for guard in window["exact_guards"]
                if guard["segment"] == number
            ),
            "preset": "odyssee-ulysse",
            "voice": "fr-FR-HenriNeural",
            "provider": "edge",
            "rate": override["rate"],
            "pitch": override["pitch"],
            "volume": override["volume"],
            "pause_after_ms": int(override["pause_after_ms"]),
            "language_locale": "fr-FR",
        }
        observed = {
            "segment": number,
            "speaker": segment.get("speaker"),
            "text": segment.get("text"),
            "preset": segment.get("preset"),
            "voice": ulysse.get("voice"),
            "provider": ulysse.get("provider", "edge"),
            "rate": segment.get("rate"),
            "pitch": segment.get("pitch"),
            "volume": segment.get("volume"),
            "pause_after_ms": segment.get("pause_after_ms"),
            "language_locale": segment.get("language_locale"),
        }
        if observed != expected:
            raise RepairError(
                f"Ulysse Round 2 setting drift at segment {number}: "
                f"{observed!r} != {expected!r}"
            )
        result.append(observed)
    return result


def _telemaque_snapshot(program, voice_pack, window):
    presets = _preset_map(voice_pack)
    telemaque = presets.get("odyssee-telemaque")
    if not telemaque:
        raise RepairError("Télémaque preset missing")
    observed_preset = {
        key: telemaque.get(key)
        for key in ("voice", "rate", "pitch", "volume", "provider")
    }
    if observed_preset != EXPECTED_TELEMAQUE_PRESET:
        raise RepairError(
            f"Télémaque preset drift: {observed_preset!r}"
        )

    start = int(window["range"]["start_segment"])
    by_abs = _absolute_segments(program, start)
    guards = {
        int(item["segment"]): item
        for item in window["exact_guards"]
    }
    result = []
    actual_numbers = tuple(
        number
        for number in range(start, int(window["range"]["end_segment"]) + 1)
        if guards[number]["speaker"] == "TÉLÉMAQUE"
    )
    if actual_numbers != TELEMAQUE_SEGMENTS:
        raise RepairError("Télémaque exact segment scope drift")

    for number in TELEMAQUE_SEGMENTS:
        segment = by_abs[number]
        guard = guards[number]
        for key in ("speaker", "text", "preset"):
            if segment.get(key) != guard.get(key):
                raise RepairError(
                    f"Télémaque frozen {key} drift at segment {number}"
                )
        for forbidden in ("rate", "pitch", "volume"):
            if forbidden in segment:
                raise RepairError(
                    f"Télémaque artistic override forbidden at segment {number}"
                )
        if segment.get("language_locale") != "fr-FR":
            raise RepairError(
                f"Télémaque segment {number} must carry fr-FR transport locale"
            )
        result.append({
            "segment": number,
            "speaker": segment["speaker"],
            "text": segment["text"],
            "preset": segment["preset"],
            **observed_preset,
            "language_locale": "fr-FR",
        })
    return result


def materialize(out_dir, root=ROOT):
    root = Path(root).resolve()
    contract = load_json(CONTRACT)
    manifest = load_json(MANIFEST)
    window = father_window(contract)
    validated = r2.validate_window(window, root, manifest)
    program, voice_pack = r2.build_candidate(window, validated)

    program["id"] = "odyssee-p7-r2-father-context-repair"
    program["title"] = "P7 Round 2 father technical context repair"

    if len(program.get("segments") or []) != 19:
        raise RepairError("father repair must contain exactly S12 136-154")

    ulysse = _ulysse_snapshot(program, voice_pack, window)
    telemaque = _telemaque_snapshot(program, voice_pack, window)

    out_dir = Path(out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    program_path = out_dir / "father-context-repair.json"
    voices_path = out_dir / "father-context-repair.voices.json"
    write_json(program_path, program)
    write_json(voices_path, voice_pack)

    plan = {
        "schema": "recit.odyssee.p7_round2_telemaque_context_repair_plan.v1",
        "status": "READY_TO_RENDER_P7_R2_FATHER_CONTEXT_REPAIR",
        "engine_ref": ENGINE_REF,
        "authority_contract": str(CONTRACT.relative_to(root)),
        "authority_contract_sha256": sha256_file(CONTRACT),
        "source_program": window["source_program"],
        "source_program_git_blob_sha1": window["source_program_git_blob_sha1"],
        "range": copy.deepcopy(window["range"]),
        "program_id": program["id"],
        "program_path": str(program_path.relative_to(root)),
        "voice_pack_path": str(voices_path.relative_to(root)),
        "production_voice_pack": validated["voice_pack_path"],
        "production_voice_pack_sha256": validated["voice_pack_sha256"],
        "source_round2_release_tag": ROUND2_RELEASE_TAG,
        "source_round2_father_asset": ROUND2_FATHER_ASSET,
        "source_round2_father_sha256": ROUND2_FATHER_SHA256,
        "ulysse_round2_snapshot": ulysse,
        "ulysse_round2_snapshot_sha256": digest_json(ulysse),
        "telemaque_snapshot": telemaque,
        "telemaque_snapshot_sha256": digest_json(telemaque),
        "repair": {
            "scope": "TELEMAQUE_CONTEXT_LANGUAGE_TRANSPORT_ONLY",
            "spoken_language": "fr-FR",
            "ssml_requirement": "<lang xml:lang='fr-FR'>",
            "multilingual_voice_only": True,
            "ulysse_artistic_parameter_change": False,
            "recasting": False,
            "frozen_text_change": False,
            "provider_change": False,
            "production_program_mutation": False,
            "new_edge_tuning": False,
            "round3_edge": False,
        },
    }
    write_json(out_dir / "plan.json", plan)
    return plan


def _assert_transcript(plan, transcript):
    segments = transcript.get("segments") or []
    if len(segments) != 19:
        raise RepairError("repair transcript must contain exactly 19 segments")

    start = int(plan["range"]["start_segment"])
    by_abs = {
        start + offset: segment
        for offset, segment in enumerate(segments)
    }

    for expected in plan["ulysse_round2_snapshot"]:
        actual = by_abs[expected["segment"]]
        observed = {
            "segment": expected["segment"],
            "speaker": actual.get("speaker"),
            "text": actual.get("text"),
            "preset": actual.get("preset"),
            "voice": actual.get("voice"),
            "provider": actual.get("provider"),
            "rate": actual.get("rate"),
            "pitch": actual.get("pitch"),
            "volume": actual.get("volume"),
            "pause_after_ms": actual.get("pause_after_ms"),
            "language_locale": actual.get("language_locale"),
        }
        if observed != expected:
            raise RepairError(
                f"rendered Ulysse drift at {expected['segment']}"
            )

    for expected in plan["telemaque_snapshot"]:
        actual = by_abs[expected["segment"]]
        observed = {
            "segment": expected["segment"],
            "speaker": actual.get("speaker"),
            "text": actual.get("text"),
            "preset": actual.get("preset"),
            "voice": actual.get("voice"),
            "rate": actual.get("rate"),
            "pitch": actual.get("pitch"),
            "volume": actual.get("volume"),
            "provider": actual.get("provider"),
            "language_locale": actual.get("language_locale"),
        }
        if observed != expected:
            raise RepairError(
                f"rendered Télémaque transport drift at {expected['segment']}"
            )


def collect(plan_path, render_root, release_out, product_sha):
    plan = load_json(plan_path)
    if plan.get("status") != "READY_TO_RENDER_P7_R2_FATHER_CONTEXT_REPAIR":
        raise RepairError("repair plan is not ready")
    if plan.get("engine_ref") != ENGINE_REF:
        raise RepairError("repair engine ref drift")
    repair = plan.get("repair") or {}
    forbidden_true = (
        "ulysse_artistic_parameter_change",
        "recasting",
        "frozen_text_change",
        "provider_change",
        "production_program_mutation",
        "new_edge_tuning",
        "round3_edge",
    )
    if any(repair.get(key) is not False for key in forbidden_true):
        raise RepairError("repair scope expanded beyond technical context")

    render_dir = Path(render_root).resolve() / plan["program_id"]
    audio = render_dir / "audio.mp3"
    qa = render_dir / "qa-report.json"
    manifest = render_dir / "manifest.json"
    transcript_path = render_dir / "transcript.json"
    if not all(path.is_file() for path in (audio, qa, manifest, transcript_path)):
        raise RepairError("incomplete father context repair render")

    qa_data = load_json(qa)
    if qa_data.get("status") != "PASS":
        raise RepairError("father context repair machine QA failed")

    transcript = load_json(transcript_path)
    _assert_transcript(plan, transcript)

    release_out = Path(release_out).resolve()
    if release_out.exists():
        shutil.rmtree(release_out)
    release_out.mkdir(parents=True, exist_ok=True)

    audio_target = release_out / REPAIR_AUDIO
    qa_target = release_out / REPAIR_QA
    shutil.copy2(audio, audio_target)
    shutil.copy2(qa, qa_target)

    index = {
        "schema": "recit.odyssee.p7_round2_telemaque_context_repair_index.v1",
        "status": "machine-ready-p7-r2-father-context-repair",
        "render_product_sha": product_sha,
        "engine_ref": ENGINE_REF,
        "authority_contract": plan["authority_contract"],
        "authority_contract_sha256": plan["authority_contract_sha256"],
        "source_program": plan["source_program"],
        "source_program_git_blob_sha1": plan["source_program_git_blob_sha1"],
        "range": plan["range"],
        "source_round2": {
            "release_tag": plan["source_round2_release_tag"],
            "father_asset": plan["source_round2_father_asset"],
            "father_sha256": plan["source_round2_father_sha256"],
        },
        "repair_audio": REPAIR_AUDIO,
        "repair_audio_sha256": sha256_file(audio_target),
        "qa": REPAIR_QA,
        "qa_sha256": sha256_file(qa_target),
        "qa_status": "PASS",
        "render_manifest_sha256": sha256_file(manifest),
        "transcript_sha256": sha256_file(transcript_path),
        "ulysse_round2_snapshot_sha256": plan["ulysse_round2_snapshot_sha256"],
        "telemaque_snapshot_sha256": plan["telemaque_snapshot_sha256"],
        "telemaque_segments": list(TELEMAQUE_SEGMENTS),
        "telemaque_voice": EXPECTED_TELEMAQUE_PRESET["voice"],
        "telemaque_spoken_language": "fr-FR",
        "telemaque_transport": "SSML_LANG_FR_FR_MULTILINGUAL_ONLY",
        "ulysse_artistic_parameter_change": False,
        "recasting": False,
        "frozen_text_change": False,
        "provider_change": False,
        "production_program_mutation": False,
        "new_edge_tuning": False,
        "round3_edge": False,
        "frozen_round2_artistic_fail_evidence_preserved": True,
        "human_confirmation_scope": "FATHER_CONTEXT_TECHNICAL_INTEGRITY_ONLY",
    }
    write_json(release_out / REPAIR_INDEX, index)
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="P7 Round 2 father Télémaque technical context repair"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("materialize")
    prep.add_argument("--out", required=True)
    collect_cmd = sub.add_parser("collect")
    collect_cmd.add_argument("--plan", required=True)
    collect_cmd.add_argument("--render-root", required=True)
    collect_cmd.add_argument("--release-out", required=True)
    collect_cmd.add_argument("--product-sha", required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "materialize":
            result = materialize(args.out)
        else:
            result = collect(
                args.plan,
                args.render_root,
                args.release_out,
                args.product_sha,
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (
        RepairError,
        r2.P7Round2Error,
        r2.base.P7RenderError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
