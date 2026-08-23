#!/usr/bin/env python3
import argparse
import copy
import glob
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HELD_PAUSE_MS = 1600


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_json(command):
    completed = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
    return json.loads(completed.stdout)


def production_specs():
    return [(path, load_json(path)) for path in sorted(ROOT.glob("series/*/production.json"))]


def resolve_spec(path: Path, raw):
    if raw.get("version") != 1:
        raise ValueError(f"{path}: version must be 1")
    if raw.get("strategy") != "scene-sequences":
        raise ValueError(f"{path}: strategy must be scene-sequences")
    program = (path.parent / raw.get("program", "")).resolve()
    direction = (path.parent / raw.get("direction", "")).resolve()
    if not program.is_file():
        raise ValueError(f"{path}: program not found: {program}")
    if not direction.is_file():
        raise ValueError(f"{path}: direction not found: {direction}")
    held_pause_ms = int(raw.get("held_pause_ms", DEFAULT_HELD_PAUSE_MS))
    if not 750 <= held_pause_ms <= 4000:
        raise ValueError(f"{path}: held_pause_ms must be between 750 and 4000")
    return {
        "path": path,
        "raw": raw,
        "program_path": program,
        "direction_path": direction,
        "held_pause_ms": held_pause_ms,
    }


def scene_spans(segments):
    if not segments:
        return []
    spans = []
    start = 1
    scene = segments[0].get("scene") or "Sans scène"
    for index, segment in enumerate(segments[1:], start=2):
        next_scene = segment.get("scene") or "Sans scène"
        if next_scene != scene:
            spans.append({"start": start, "end": index - 1, "scenes": [scene]})
            start = index
            scene = next_scene
    spans.append({"start": start, "end": len(segments), "scenes": [scene]})
    return spans


def sound_beats(direction):
    return [
        beat for beat in direction.get("beats", [])
        if beat.get("attention_owner") == "sound" and beat.get("sound") and beat.get("after_segment")
    ]


def merge_bridge_boundaries(spans, direction):
    spans = copy.deepcopy(spans)
    for beat in sound_beats(direction):
        anchor = int(beat["after_segment"])
        for index, span in enumerate(spans):
            if span["start"] <= anchor <= span["end"]:
                if anchor == span["end"] and index + 1 < len(spans):
                    following = spans[index + 1]
                    span["end"] = following["end"]
                    span["scenes"].extend(following["scenes"])
                    spans.pop(index + 1)
                break
    return spans


def validate_inputs(spec):
    program = load_json(spec["program_path"])
    direction = load_json(spec["direction_path"])
    if program.get("id") != direction.get("id"):
        raise ValueError(f"{spec['path']}: program id and direction id differ")
    segments = program.get("segments") or []
    if not segments:
        raise ValueError(f"{spec['path']}: program has no segments")
    if program.get("soundscape") or program.get("ambience"):
        raise ValueError(f"{spec['path']}: scene-sequences v1 expects a clean canonical program")
    for beat in direction.get("beats", []):
        anchor = beat.get("after_segment")
        if anchor is not None and (not isinstance(anchor, int) or not 1 <= anchor <= len(segments)):
            raise ValueError(f"{spec['path']}: invalid direction anchor {anchor}")
    spans = merge_bridge_boundaries(scene_spans(segments), direction)
    for beat in sound_beats(direction):
        anchor = int(beat["after_segment"])
        span = next(item for item in spans if item["start"] <= anchor <= item["end"])
        if anchor >= span["end"]:
            raise ValueError(f"{spec['path']}: bridge after segment {anchor} has no following segment inside its sequence")
    return program, direction, spans


def sequence_event(beat, local_anchor):
    return {
        "sound": beat["sound"],
        "role": "bridge",
        "after_segment": local_anchor,
        "foreground_ms": 2600,
        "carry_through_segments": 1,
        "tail_ms": 900,
        "gain_db": -16,
        "placement": "center",
        "fade_in_ms": 120,
        "fade_out_ms": 1000,
    }


def derive_sequences(spec, work_root: Path):
    program, direction, spans = validate_inputs(spec)
    source_id = program["id"]
    program_dir = work_root / source_id / "programs"
    program_dir.mkdir(parents=True, exist_ok=True)
    derived = []

    for sequence_number, span in enumerate(spans, start=1):
        sequence = copy.deepcopy(program)
        sequence_id = f".seq--{source_id}--{sequence_number:02d}"
        sequence["id"] = sequence_id
        sequence["title"] = f"{program['title']} — séquence interne {sequence_number}"
        sequence["segments"] = copy.deepcopy(program["segments"][span["start"] - 1:span["end"]])
        events = []
        applied_beats = []
        for beat in direction.get("beats", []):
            anchor = beat.get("after_segment")
            if not isinstance(anchor, int) or not span["start"] <= anchor <= span["end"]:
                continue
            local_anchor = anchor - span["start"] + 1
            if beat.get("id"):
                applied_beats.append(beat["id"])
            if beat.get("attention_owner") == "silence" and beat.get("exit") == "held-pause":
                segment = sequence["segments"][local_anchor - 1]
                segment["pause_after_ms"] = max(int(segment.get("pause_after_ms", 0)), spec["held_pause_ms"])
            if beat.get("attention_owner") == "sound" and beat.get("sound"):
                if local_anchor >= len(sequence["segments"]):
                    raise ValueError(f"{spec['path']}: bridge {beat.get('id')} crosses a sequence boundary")
                events.append(sequence_event(beat, local_anchor))
        if events:
            sequence["schema_version"] = 6
            sequence["soundscape"] = {"events": events, "ducking": "speech"}
        sequence_path = program_dir / f"seq-{sequence_number:02d}.json"
        write_json(sequence_path, sequence)
        derived.append({
            "number": sequence_number,
            "id": sequence_id,
            "path": sequence_path,
            "start_segment": span["start"],
            "end_segment": span["end"],
            "scenes": span["scenes"],
            "applied_beats": applied_beats,
        })

    plan = {
        "program_id": source_id,
        "title": program["title"],
        "program_path": str(spec["program_path"].relative_to(ROOT)),
        "direction_path": str(spec["direction_path"].relative_to(ROOT)),
        "sequence_count": len(derived),
        "sequences": [{k: v for k, v in item.items() if k != "path"} for item in derived],
    }
    write_json(work_root / source_id / "sequence-plan.json", plan)
    return program, derived, plan


def combine_transcripts(source_program, sequence_results, final_dir: Path):
    segments = []
    program_schema_version = source_program.get("schema_version", 1)
    for item in sequence_results:
        transcript = load_json(item["audio_dir"] / "transcript.json")
        program_schema_version = max(program_schema_version, transcript.get("program_schema_version", 1))
        segments.extend(transcript.get("segments") or [])
    write_json(final_dir / "transcript.json", {
        "schema_version": 1,
        "program_schema_version": program_schema_version,
        "id": source_program["id"],
        "title": source_program["title"],
        "language": source_program.get("language"),
        "sources": source_program.get("sources", []),
        "segments": segments,
    })


def production_fingerprint(spec, sequence_results):
    payload = {
        "spec_sha256": sha256_file(spec["path"]),
        "program_sha256": sha256_file(spec["program_path"]),
        "direction_sha256": sha256_file(spec["direction_path"]),
        "sequence_audio": [sha256_file(item["audio_dir"] / "audio.mp3") for item in sequence_results],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def produce_managed(spec, output_root: Path, sounds_path=None):
    work_root = output_root / ".production"
    source_program, derived, plan = derive_sequences(spec, work_root)
    sequence_results = []
    for item in derived:
        command = ["audio-engine", "render", str(item["path"]), "--out", str(output_root)]
        if sounds_path:
            command.extend(["--sounds", str(sounds_path)])
        manifest = run_json(command)
        sequence_results.append({
            **item,
            "cache_hit": bool(manifest.get("cache_hit")),
            "audio_dir": output_root / item["id"],
            "duration_seconds": (manifest.get("audio") or {}).get("duration_seconds"),
        })

    final_dir = output_root / source_program["id"]
    final_dir.mkdir(parents=True, exist_ok=True)
    fingerprint = production_fingerprint(spec, sequence_results)
    fingerprint_path = final_dir / ".production-fingerprint.json"
    cached = False
    if fingerprint_path.exists() and (final_dir / "audio.mp3").exists() and (final_dir / "manifest.json").exists():
        try:
            cached = load_json(fingerprint_path).get("fingerprint") == fingerprint
        except Exception:
            cached = False

    if not cached:
        assembly_dir = work_root / source_program["id"]
        assembly_path = assembly_dir / "assembly.json"
        inputs = [
            {"file": os.path.relpath(item["audio_dir"] / "audio.mp3", assembly_dir), "pause_after_ms": 0}
            for item in sequence_results
        ]
        write_json(assembly_path, {
            "schema_version": 1,
            "id": source_program["id"],
            "profile": source_program.get("profile", "speech"),
            "inputs": inputs,
        })
        run_json(["audio-engine", "assemble", str(assembly_path), "--out", str(output_root)])
        combine_transcripts(source_program, sequence_results, final_dir)
        manifest = load_json(final_dir / "manifest.json")
        manifest["transcript"] = "transcript.json"
        manifest["production"] = {
            "strategy": "scene-sequences",
            "source_program": str(spec["program_path"].relative_to(ROOT)),
            "direction": str(spec["direction_path"].relative_to(ROOT)),
            "sequence_count": len(sequence_results),
            "sequence_ids": [item["id"] for item in sequence_results],
        }
        write_json(final_dir / "manifest.json", manifest)
        write_json(fingerprint_path, {"fingerprint": fingerprint})

    return {
        "source": str(spec["program_path"].relative_to(ROOT)),
        "id": source_program["id"],
        "cache_hit": cached,
        "production": "scene-sequences",
        "sequence_count": len(sequence_results),
        "sequence_cache_hits": sum(1 for item in sequence_results if item["cache_hit"]),
        "sequence_plan": plan,
    }


def render_unmanaged(source: Path, output_root: Path, sounds_path=None):
    command = ["audio-engine", "render", str(source), "--out", str(output_root)]
    if sounds_path:
        command.extend(["--sounds", str(sounds_path)])
    manifest = run_json(command)
    return {"source": str(source.relative_to(ROOT)), "id": manifest["id"], "cache_hit": bool(manifest.get("cache_hit"))}


def validate_all():
    summaries = []
    managed = set()
    for path, raw in production_specs():
        spec = resolve_spec(path, raw)
        program, direction, spans = validate_inputs(spec)
        relative = str(spec["program_path"].relative_to(ROOT))
        if relative in managed:
            raise ValueError(f"duplicate managed program: {relative}")
        managed.add(relative)
        summaries.append({
            "program": relative,
            "id": program["id"],
            "strategy": raw["strategy"],
            "segments": len(program["segments"]),
            "derived_sequences": len(spans),
            "direction_beats": len(direction.get("beats", [])),
        })
    print(json.dumps({"status": "valid", "managed_programs": len(summaries), "programs": summaries}, ensure_ascii=False, indent=2))
    return 0


def run_all(source_glob, output_root, sounds_path=None):
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    managed = {}
    for path, raw in production_specs():
        spec = resolve_spec(path, raw)
        relative = str(spec["program_path"].relative_to(ROOT))
        if relative in managed:
            raise ValueError(f"duplicate managed program: {relative}")
        managed[relative] = spec

    sources = sorted(Path(path).resolve() for path in glob.glob(source_glob, recursive=True) if Path(path).is_file())
    completed, failures = [], []
    for source in sources:
        relative = str(source.relative_to(ROOT))
        try:
            if relative in managed:
                completed.append(produce_managed(managed[relative], output_root, sounds_path=sounds_path))
            else:
                completed.append(render_unmanaged(source, output_root, sounds_path=sounds_path))
        except Exception as exc:
            failures.append({"source": relative, "error": str(exc)})

    status = "success"
    if not sources:
        status = "empty"
    elif failures and completed:
        status = "partial"
    elif failures:
        status = "failed"
    report = {
        "schema_version": 1,
        "status": status,
        "source_count": len(sources),
        "success_count": len(completed),
        "rendered_count": sum(1 for item in completed if not item.get("cache_hit")),
        "cached_count": sum(1 for item in completed if item.get("cache_hit")),
        "failure_count": len(failures),
        "managed_count": len(managed),
        "completed": completed,
        "failures": failures,
    }
    write_json(output_root / "render-report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description="Minimal caller-owned production orchestration")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    run = sub.add_parser("run")
    run.add_argument("--source-glob", default="series/**/audio/*.json")
    run.add_argument("--out", default="generated/audio")
    run.add_argument("--sounds", default=None)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            return validate_all()
        return run_all(args.source_glob, Path(args.out), sounds_path=Path(args.sounds) if args.sounds else None)
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
