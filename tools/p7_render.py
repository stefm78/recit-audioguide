#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "series/odyssee/review/P7_ULYSSE_PERFORMANCE_CONTINUITY_V1.json"
MANIFEST = ROOT / "series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json"
EXPECTED_STATUS = "P7_READY_FOR_STREAM3_RENDER"
EXPECTED_WINDOWS = ("storyteller", "loss", "father", "authority")
ENGINE_REF = "f14a941d9218c2e9e632d7198557e7a3e48ff894"


class P7RenderError(ValueError):
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


def git_blob_sha1(path, root=ROOT):
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        rel = path.relative_to(root)
    except ValueError as exc:
        raise P7RenderError(f"path escapes repository root: {path}") from exc
    probe = subprocess.run(
        ["git", "hash-object", "--no-filters", str(rel)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if probe.returncode != 0:
        raise P7RenderError(
            f"cannot compute Git blob for {rel}: {(probe.stderr or '').strip()}"
        )
    return probe.stdout.strip()


def _preset_map(voice_pack):
    presets = voice_pack.get("presets")
    if not isinstance(presets, list):
        raise P7RenderError("voice pack presets must be an array")
    result = {}
    for preset in presets:
        pid = preset.get("id") if isinstance(preset, dict) else None
        if not isinstance(pid, str) or not pid:
            raise P7RenderError("voice pack preset id missing")
        if pid in result:
            raise P7RenderError(f"duplicate voice preset: {pid}")
        result[pid] = preset
    return result


def _current_unit(manifest, source_program):
    matches = [
        unit
        for unit in manifest.get("units", [])
        if unit.get("program") == source_program
    ]
    if len(matches) != 1:
        raise P7RenderError(
            f"source Program {source_program!r} must map to exactly one Production unit"
        )
    return matches[0]


def validate_window(window, root, manifest, blob_fn=git_blob_sha1):
    source_rel = window["source_program"]
    source_path = root / source_rel
    if not source_path.is_file():
        raise P7RenderError(f"source Program missing: {source_rel}")
    actual_blob = blob_fn(source_path, root)
    expected_blob = window.get("source_program_git_blob_sha1")
    if actual_blob != expected_blob:
        raise P7RenderError(
            f"{window['id']} source Program blob drift: {actual_blob} != {expected_blob}"
        )

    program = load_json(source_path)
    start = int(window["range"]["start_segment"])
    end = int(window["range"]["end_segment"])
    guards = window.get("exact_guards") or []
    if len(guards) != end - start + 1:
        raise P7RenderError(f"{window['id']} exact guard count mismatch")

    observed_ulysse = []
    for expected in guards:
        segment_no = int(expected["segment"])
        if not start <= segment_no <= end:
            raise P7RenderError(f"{window['id']} guard outside frozen range")
        try:
            actual = program["segments"][segment_no - 1]
        except (KeyError, IndexError) as exc:
            raise P7RenderError(
                f"{window['id']} missing source segment {segment_no}"
            ) from exc
        for field in ("speaker", "text", "preset"):
            if actual.get(field) != expected.get(field):
                raise P7RenderError(
                    f"{window['id']} segment {segment_no} {field} drift"
                )
        if expected["speaker"] == "ULYSSE":
            observed_ulysse.append(segment_no)

    if observed_ulysse != list(window.get("ulysse_segments") or []):
        raise P7RenderError(f"{window['id']} Ulysse segment scope drift")

    unit = _current_unit(manifest, source_rel)
    voice_rel = unit.get("voice_pack")
    voice_path = root / voice_rel
    if not voice_path.is_file():
        raise P7RenderError(f"Production voice pack missing: {voice_rel}")
    voice_sha = sha256_file(voice_path)
    if voice_sha != unit.get("voice_pack_sha256"):
        raise P7RenderError(f"{window['id']} Production voice pack hash drift")
    voice_pack = load_json(voice_path)
    presets = _preset_map(voice_pack)
    ulysse = presets.get("odyssee-ulysse")
    if not ulysse:
        raise P7RenderError(f"{window['id']} current Ulysse preset missing")

    baseline = window["A"]["ulysse"]
    for field in ("voice", "rate", "pitch", "volume"):
        if ulysse.get(field) != baseline.get(field):
            raise P7RenderError(
                f"{window['id']} baseline Ulysse {field} drift: "
                f"{ulysse.get(field)!r} != {baseline.get(field)!r}"
            )
    if ulysse.get("provider", "edge") != "edge":
        raise P7RenderError(f"{window['id']} Ulysse baseline is no longer Edge")

    directed = window["B"]["ulysse"]
    if directed.get("voice") != "fr-FR-HenriNeural":
        raise P7RenderError(f"{window['id']} B must preserve Henri identity")
    pause_map = window["B"].get("ulysse_pause_after_ms") or {}
    if {int(key) for key in pause_map} != set(observed_ulysse):
        raise P7RenderError(f"{window['id']} B pause map must cover exact Ulysse scope")

    return {
        "program": program,
        "voice_pack": voice_pack,
        "voice_pack_path": voice_rel,
        "voice_pack_sha256": voice_sha,
        "start": start,
        "end": end,
    }


def build_variant(window, validated, variant):
    if variant not in ("A", "B"):
        raise P7RenderError(f"unsupported P7 variant: {variant}")
    start = validated["start"]
    end = validated["end"]
    source = validated["program"]
    program = {
        "schema_version": source["schema_version"],
        "id": f"odyssee-p7-{window['id']}-{variant.lower()}",
        "title": f"P7 {window['id']} {variant}",
        "language": source["language"],
        "profile": source.get("profile", "speech"),
        "acoustic_space": "dry",
        "sources": copy.deepcopy(source.get("sources") or []),
        "segments": copy.deepcopy(source["segments"][start - 1:end]),
    }
    voice_pack = copy.deepcopy(validated["voice_pack"])

    if variant == "B":
        directed = window["B"]["ulysse"]
        preset = _preset_map(voice_pack)["odyssee-ulysse"]
        for field in ("voice", "rate", "pitch", "volume"):
            preset[field] = directed[field]
        pause_map = {
            int(segment): int(value)
            for segment, value in window["B"]["ulysse_pause_after_ms"].items()
        }
        ulysse_scope = set(window["ulysse_segments"])
        for offset, segment in enumerate(program["segments"], start=start):
            if offset in ulysse_scope:
                segment["pause_after_ms"] = pause_map[offset]

    return program, voice_pack


def materialize(out_dir, root=ROOT, contract_path=CONTRACT, manifest_path=MANIFEST):
    root = Path(root).resolve()
    contract = load_json(contract_path)
    manifest = load_json(manifest_path)
    if contract.get("status") != EXPECTED_STATUS:
        raise P7RenderError(
            f"P7 contract status must be {EXPECTED_STATUS}, got {contract.get('status')}"
        )
    windows = contract.get("round_1", {}).get("windows") or []
    if tuple(window.get("id") for window in windows) != EXPECTED_WINDOWS:
        raise P7RenderError("P7 Round 1 window order/scope drift")

    out_dir = Path(out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for window in windows:
        validated = validate_window(window, root, manifest)
        for variant in ("A", "B"):
            program, voice_pack = build_variant(window, validated, variant)
            program_path = out_dir / f"{program['id']}.json"
            voices_path = out_dir / f"{program['id']}.voices.json"
            write_json(program_path, program)
            write_json(voices_path, voice_pack)
            assets = window["output_assets"]
            entries.append({
                "state": window["id"],
                "variant": variant,
                "program_id": program["id"],
                "program_path": str(program_path),
                "voice_pack_path": str(voices_path),
                "source_program": window["source_program"],
                "source_program_git_blob_sha1": window["source_program_git_blob_sha1"],
                "production_voice_pack": validated["voice_pack_path"],
                "production_voice_pack_sha256": validated["voice_pack_sha256"],
                "output_asset": assets[variant],
                "qa_asset": assets[f"qa_{variant}"],
            })

    plan = {
        "schema": "recit.odyssee.p7_round1_render_plan.v1",
        "status": "READY_TO_RENDER_P7_ROUND1",
        "authority_contract": str(Path(contract_path).resolve().relative_to(root)),
        "authority_contract_sha256": sha256_file(contract_path),
        "engine_ref": ENGINE_REF,
        "entry_count": len(entries),
        "entries": entries,
    }
    write_json(out_dir / "plan.json", plan)
    return plan


def collect(plan_path, render_root, release_out, product_sha):
    plan = load_json(plan_path)
    if plan.get("status") != "READY_TO_RENDER_P7_ROUND1":
        raise P7RenderError("P7 render plan is not ready")
    if plan.get("entry_count") != 8 or len(plan.get("entries") or []) != 8:
        raise P7RenderError("P7 release requires exactly eight A/B renders")

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
        if not audio.is_file() or not qa.is_file() or not manifest.is_file():
            raise P7RenderError(f"incomplete render for {entry['program_id']}")
        qa_data = load_json(qa)
        if qa_data.get("status") != "PASS":
            raise P7RenderError(f"machine QA failed for {entry['program_id']}")

        audio_target = release_out / entry["output_asset"]
        qa_target = release_out / entry["qa_asset"]
        shutil.copy2(audio, audio_target)
        shutil.copy2(qa, qa_target)
        assets.append({
            "state": entry["state"],
            "variant": entry["variant"],
            "audio": entry["output_asset"],
            "audio_sha256": sha256_file(audio_target),
            "qa": entry["qa_asset"],
            "qa_sha256": sha256_file(qa_target),
            "qa_status": "PASS",
            "render_manifest_sha256": sha256_file(manifest),
            "source_program": entry["source_program"],
            "source_program_git_blob_sha1": entry["source_program_git_blob_sha1"],
            "production_voice_pack": entry["production_voice_pack"],
            "production_voice_pack_sha256": entry["production_voice_pack_sha256"],
        })

    index = {
        "schema": "recit.odyssee.p7_review_index.v1",
        "status": "machine-ready-p7-review-assets",
        "round": 1,
        "authority_product_sha": "203a196941c48d80c7e238e3c8596d94d15b29ce",
        "render_product_sha": product_sha,
        "engine_ref": plan["engine_ref"],
        "authority_contract": plan["authority_contract"],
        "authority_contract_sha256": plan["authority_contract_sha256"],
        "asset_count": 16,
        "states": list(EXPECTED_WINDOWS),
        "assets": assets,
        "production_programs_mutated": False,
        "recasting": False,
        "decorative_sound": False,
        "human_review_required": True,
        "decision_authority": "series/odyssee/review/P7_ULYSSE_PERFORMANCE_CONTINUITY_V1.json",
    }
    write_json(release_out / "p7-review-index.json", index)
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(description="P7 Ulysse continuity render staging")
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
    except (P7RenderError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
