#!/usr/bin/env python3
import argparse
import copy
import json
import shutil
import sys
from pathlib import Path

from tools import p7_render as base

ROOT = base.ROOT
CONTRACT = ROOT / "series/odyssee/review/P7_ULYSSE_PERFORMANCE_CONTINUITY_ROUND2_V1.json"
MANIFEST = base.MANIFEST
EXPECTED_STATUS = "P7_ROUND2_READY_FOR_STREAM3_RENDER"
EXPECTED_WINDOWS = ("storyteller", "loss", "father", "authority")
ENGINE_REF = base.ENGINE_REF


class P7Round2Error(ValueError):
    pass


def load_json(path):
    return base.load_json(path)


def write_json(path, data):
    return base.write_json(path, data)


def _production_voice_pack(window, root, manifest):
    unit = base._current_unit(manifest, window["source_program"])
    voice_rel = unit.get("voice_pack")
    voice_path = root / voice_rel
    if not voice_path.is_file():
        raise P7Round2Error(f"Production voice pack missing: {voice_rel}")
    voice_sha = base.sha256_file(voice_path)
    if voice_sha != unit.get("voice_pack_sha256"):
        raise P7Round2Error(f"{window['id']} Production voice pack hash drift")
    voice_pack = load_json(voice_path)
    presets = base._preset_map(voice_pack)
    ulysse = presets.get("odyssee-ulysse")
    if not ulysse:
        raise P7Round2Error(f"{window['id']} current Ulysse preset missing")
    if ulysse.get("voice") != "fr-FR-HenriNeural":
        raise P7Round2Error(f"{window['id']} Ulysse identity drift")
    if ulysse.get("provider", "edge") != "edge":
        raise P7Round2Error(f"{window['id']} Ulysse provider drift")
    return voice_pack, voice_rel, voice_sha


def validate_window(window, root, manifest, blob_fn=base.git_blob_sha1):
    source_rel = window["source_program"]
    source_path = root / source_rel
    if not source_path.is_file():
        raise P7Round2Error(f"source Program missing: {source_rel}")
    actual_blob = blob_fn(source_path, root)
    if actual_blob != window.get("source_program_git_blob_sha1"):
        raise P7Round2Error(f"{window['id']} source Program blob drift")

    program = load_json(source_path)
    start = int(window["range"]["start_segment"])
    end = int(window["range"]["end_segment"])
    guards = window.get("exact_guards") or []
    if len(guards) != end - start + 1:
        raise P7Round2Error(f"{window['id']} guard count mismatch")

    observed_ulysse = []
    for expected in guards:
        number = int(expected["segment"])
        if not start <= number <= end:
            raise P7Round2Error(f"{window['id']} guard outside range")
        try:
            actual = program["segments"][number - 1]
        except (KeyError, IndexError) as exc:
            raise P7Round2Error(f"{window['id']} missing segment {number}") from exc
        for field in ("speaker", "text", "preset"):
            if actual.get(field) != expected.get(field):
                raise P7Round2Error(
                    f"{window['id']} segment {number} {field} drift"
                )
        if actual.get("speaker") == "ULYSSE":
            observed_ulysse.append(number)

    if observed_ulysse != list(window.get("ulysse_segments") or []):
        raise P7Round2Error(f"{window['id']} Ulysse scope drift")

    overrides = window.get("C", {}).get("segment_overrides") or {}
    if {int(key) for key in overrides} != set(observed_ulysse):
        raise P7Round2Error(
            f"{window['id']} Round 2 overrides must cover exact Ulysse scope"
        )
    for number in observed_ulysse:
        item = overrides[str(number)]
        if set(item) != {"rate", "pitch", "volume", "pause_after_ms"}:
            raise P7Round2Error(
                f"{window['id']} segment {number} override fields drift"
            )
        if not isinstance(item["pause_after_ms"], int) or item["pause_after_ms"] < 0:
            raise P7Round2Error(
                f"{window['id']} segment {number} invalid pause"
            )

    voice_pack, voice_rel, voice_sha = _production_voice_pack(
        window, root, manifest
    )
    return {
        "program": program,
        "voice_pack": voice_pack,
        "voice_pack_path": voice_rel,
        "voice_pack_sha256": voice_sha,
        "start": start,
        "end": end,
    }


def build_candidate(window, validated):
    start = validated["start"]
    end = validated["end"]
    source = validated["program"]
    program = {
        "schema_version": source["schema_version"],
        "id": f"odyssee-p7-r2-{window['id']}-c",
        "title": f"P7 Round 2 {window['id']} C",
        "language": source["language"],
        "profile": source.get("profile", "speech"),
        "acoustic_space": "dry",
        "sources": copy.deepcopy(source.get("sources") or []),
        "segments": copy.deepcopy(source["segments"][start - 1:end]),
    }
    voice_pack = copy.deepcopy(validated["voice_pack"])
    presets = base._preset_map(voice_pack)
    overrides = {
        int(number): values
        for number, values in window["C"]["segment_overrides"].items()
    }
    ulysse_scope = set(window["ulysse_segments"])

    for absolute, segment in enumerate(program["segments"], start=start):
        # P7-only technical integrity guard: force French SSML locale on Edge
        # without changing voice, text, rate, pitch, volume or preset for context.
        preset = presets.get(segment.get("preset"))
        provider = segment.get("provider") or (
            preset.get("provider", "edge") if preset else "edge"
        )
        if provider == "edge":
            segment["language_locale"] = "fr-FR"

        if absolute in ulysse_scope:
            values = overrides[absolute]
            segment["rate"] = values["rate"]
            segment["pitch"] = values["pitch"]
            segment["volume"] = values["volume"]
            segment["pause_after_ms"] = int(values["pause_after_ms"])

    return program, voice_pack


def materialize(out_dir, root=ROOT, contract_path=CONTRACT, manifest_path=MANIFEST):
    root = Path(root).resolve()
    contract = load_json(contract_path)
    manifest = load_json(manifest_path)
    if contract.get("status") != EXPECTED_STATUS:
        raise P7Round2Error(
            f"Round 2 status must be {EXPECTED_STATUS}, got {contract.get('status')}"
        )
    windows = contract.get("windows") or []
    if tuple(w.get("id") for w in windows) != EXPECTED_WINDOWS:
        raise P7Round2Error("Round 2 window order/scope drift")

    out_dir = Path(out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for window in windows:
        validated = validate_window(window, root, manifest)
        program, voice_pack = build_candidate(window, validated)
        program_path = out_dir / f"{program['id']}.json"
        voices_path = out_dir / f"{program['id']}.voices.json"
        write_json(program_path, program)
        write_json(voices_path, voice_pack)
        entries.append({
            "state": window["id"],
            "variant": "C",
            "program_id": program["id"],
            "program_path": str(program_path.relative_to(root)),
            "voice_pack_path": str(voices_path.relative_to(root)),
            "source_program": window["source_program"],
            "source_program_git_blob_sha1": window["source_program_git_blob_sha1"],
            "production_voice_pack": validated["voice_pack_path"],
            "production_voice_pack_sha256": validated["voice_pack_sha256"],
            "round1_reference_asset": window["round1_reference_asset"],
            "output_asset": window["output_assets"]["C"],
            "qa_asset": window["output_assets"]["qa_C"],
        })

    plan = {
        "schema": "recit.odyssee.p7_round2_render_plan.v1",
        "status": "READY_TO_RENDER_P7_ROUND2",
        "authority_contract": str(Path(contract_path).resolve().relative_to(root)),
        "authority_contract_sha256": base.sha256_file(contract_path),
        "engine_ref": ENGINE_REF,
        "round1_release_tag": contract["round1_release_tag"],
        "entry_count": len(entries),
        "entries": entries,
        "production_programs_mutated": False,
        "recasting": False,
        "frozen_text_change": False,
        "language_locale_override": "fr-FR",
    }
    write_json(out_dir / "plan.json", plan)
    return plan


def collect(plan_path, render_root, release_out, product_sha):
    plan = load_json(plan_path)
    if plan.get("status") != "READY_TO_RENDER_P7_ROUND2":
        raise P7Round2Error("Round 2 render plan is not ready")
    if plan.get("entry_count") != 4 or len(plan.get("entries") or []) != 4:
        raise P7Round2Error("Round 2 requires exactly four C renders")

    render_root = Path(render_root).resolve()
    release_out = Path(release_out).resolve()
    if release_out.exists():
        shutil.rmtree(release_out)
    release_out.mkdir(parents=True, exist_ok=True)

    assets = []
    for entry in plan["entries"]:
        render_dir = render_root / entry["program_id"]
        audio = render_dir / "audio.mp3"
        qa = render_dir / "qa-report.json"
        manifest = render_dir / "manifest.json"
        transcript = render_dir / "transcript.json"
        if not all(p.is_file() for p in (audio, qa, manifest, transcript)):
            raise P7Round2Error(f"incomplete render for {entry['program_id']}")
        qa_data = load_json(qa)
        if qa_data.get("status") != "PASS":
            raise P7Round2Error(f"machine QA failed for {entry['program_id']}")

        transcript_data = load_json(transcript)
        for segment in transcript_data.get("segments") or []:
            if segment.get("provider") == "edge" and segment.get("language_locale") != "fr-FR":
                raise P7Round2Error(
                    f"missing explicit French locale in {entry['program_id']}"
                )

        audio_target = release_out / entry["output_asset"]
        qa_target = release_out / entry["qa_asset"]
        shutil.copy2(audio, audio_target)
        shutil.copy2(qa, qa_target)
        assets.append({
            "state": entry["state"],
            "variant": "C",
            "audio": entry["output_asset"],
            "audio_sha256": base.sha256_file(audio_target),
            "qa": entry["qa_asset"],
            "qa_sha256": base.sha256_file(qa_target),
            "qa_status": "PASS",
            "render_manifest_sha256": base.sha256_file(manifest),
            "transcript_sha256": base.sha256_file(transcript),
            "round1_reference_asset": entry["round1_reference_asset"],
            "source_program": entry["source_program"],
            "source_program_git_blob_sha1": entry["source_program_git_blob_sha1"],
            "production_voice_pack": entry["production_voice_pack"],
            "production_voice_pack_sha256": entry["production_voice_pack_sha256"],
        })

    index = {
        "schema": "recit.odyssee.p7_round2_review_index.v1",
        "status": "machine-ready-p7-round2-review-assets",
        "round": 2,
        "render_product_sha": product_sha,
        "engine_ref": plan["engine_ref"],
        "authority_contract": plan["authority_contract"],
        "authority_contract_sha256": plan["authority_contract_sha256"],
        "round1_release_tag": plan["round1_release_tag"],
        "asset_count": 8,
        "states": list(EXPECTED_WINDOWS),
        "assets": assets,
        "production_programs_mutated": False,
        "recasting": False,
        "frozen_text_change": False,
        "language_locale_override": "fr-FR",
        "human_review_required": True,
    }
    write_json(release_out / "p7-r2-review-index.json", index)
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(description="P7 Round 2 Ulysse line micro-prosody")
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
                args.plan, args.render_root, args.release_out, args.product_sha
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (P7Round2Error, base.P7RenderError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
