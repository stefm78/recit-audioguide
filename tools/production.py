#!/usr/bin/env python3
import argparse
import copy
import glob
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HELD_PAUSE_MS = 1600
LONGFORM_BRIDGE_FOREGROUND_MS = 3200
LONGFORM_BRIDGE_CARRY_MS = 7000


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    """Keep each sound-to-voice handoff inside one internal QA sequence."""
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
    for beat in sound_beats(direction):
        if int(beat["after_segment"]) >= len(segments):
            raise ValueError(f"{spec['path']}: sound bridge needs a following segment")
    return program, direction, merge_bridge_boundaries(scene_spans(segments), direction)


def bridge_event(beat):
    return {
        "sound": beat["sound"],
        "role": "bridge",
        "after_segment": int(beat["after_segment"]),
        "foreground_ms": LONGFORM_BRIDGE_FOREGROUND_MS,
        "carry_under_speech_ms": LONGFORM_BRIDGE_CARRY_MS,
        "gain_db": -16,
        "placement": "center",
        "fade_in_ms": 120,
        "fade_out_ms": 1400,
    }


def build_sequence_plan(program, direction, spans, spec):
    sequences = []
    for number, span in enumerate(spans, start=1):
        beats = []
        for beat in direction.get("beats", []):
            anchor = beat.get("after_segment")
            if isinstance(anchor, int) and span["start"] <= anchor <= span["end"] and beat.get("id"):
                beats.append(beat["id"])
        sequences.append({
            "number": number,
            "start_segment": span["start"],
            "end_segment": span["end"],
            "scenes": span["scenes"],
            "applied_beats": beats,
        })
    return {
        "program_id": program["id"],
        "title": program["title"],
        "program_path": str(spec["program_path"].relative_to(ROOT)),
        "direction_path": str(spec["direction_path"].relative_to(ROOT)),
        "sequence_count": len(sequences),
        "render_mode": "single-master",
        "sequences": sequences,
    }


def compile_program(spec, work_root: Path):
    source_program, direction, spans = validate_inputs(spec)
    compiled = copy.deepcopy(source_program)
    events = []
    for beat in direction.get("beats", []):
        anchor = beat.get("after_segment")
        if not isinstance(anchor, int):
            continue
        if beat.get("attention_owner") == "silence" and beat.get("exit") == "held-pause":
            segment = compiled["segments"][anchor - 1]
            segment["pause_after_ms"] = max(int(segment.get("pause_after_ms", 0)), spec["held_pause_ms"])
        if beat.get("attention_owner") == "sound" and beat.get("sound"):
            events.append(bridge_event(beat))
    if events:
        compiled["schema_version"] = 6
        compiled["soundscape"] = {"events": events, "ducking": "speech"}

    production_dir = work_root / source_program["id"]
    compiled_path = production_dir / "compiled-program.json"
    write_json(compiled_path, compiled)
    plan = build_sequence_plan(source_program, direction, spans, spec)
    write_json(production_dir / "sequence-plan.json", plan)
    return source_program, compiled_path, plan


def produce_managed(spec, output_root: Path, sounds_path=None):
    source_program, compiled_path, plan = compile_program(spec, output_root / ".production")
    command = ["audio-engine", "render", str(compiled_path), "--out", str(output_root)]
    if sounds_path:
        command.extend(["--sounds", str(sounds_path)])
    manifest = run_json(command)

    final_dir = output_root / source_program["id"]
    persisted = load_json(final_dir / "manifest.json")
    persisted["production"] = {
        "strategy": "scene-sequences",
        "render_mode": "single-master",
        "source_program": str(spec["program_path"].relative_to(ROOT)),
        "direction": str(spec["direction_path"].relative_to(ROOT)),
        "sequence_count": plan["sequence_count"],
    }
    write_json(final_dir / "manifest.json", persisted)

    mix = manifest.get("mix") or {}
    return {
        "source": str(spec["program_path"].relative_to(ROOT)),
        "id": source_program["id"],
        "cache_hit": bool(manifest.get("cache_hit")),
        "production": "scene-sequences",
        "render_mode": "single-master",
        "sequence_count": plan["sequence_count"],
        "voice_cache_hits": mix.get("voice_cache_hits"),
        "voice_clip_count": mix.get("voice_clip_count"),
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
            "render_mode": "single-master",
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
