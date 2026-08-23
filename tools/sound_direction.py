#!/usr/bin/env python3
"""Lightweight tooling for the editorial Sound Direction v1 contract.

The tool validates policy/review coverage and detailed sidecars. It never makes
creative decisions: those belong to the human/AI Sound Director.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODES = {"story", "visit", "route", "audiobook", "learning"}
DENSITIES = {"none", "light", "scene-rich"}
DECISIONS = {"keep", "direct", "enhance"}
ATTENTION = {"voice", "sound", "silence", "space"}
DEFAULT_CONSTRAINTS = [
    "no_narration_duplicates_obvious_sound",
    "one_primary_attention_owner_per_beat",
    "continuous_layers_need_narrative_reason",
    "silence_is_allowed",
    "measured_voice_timing_is_authoritative",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def audio_programs(root: Path):
    result = {}
    for path in sorted(root.glob("series/**/audio/*.json")):
        try:
            data = load_json(path)
        except Exception:
            continue
        program_id = data.get("id")
        if isinstance(program_id, str) and program_id:
            result[program_id] = (path, data)
    return result


def real_programs(root: Path, programs=None):
    programs = programs or audio_programs(root)
    return {
        program_id: value
        for program_id, value in programs.items()
        if "_showcase" not in value[0].parts
    }


def real_series(root: Path):
    series_root = root / "series"
    return {
        path.name
        for path in series_root.iterdir()
        if path.is_dir() and not path.name.startswith("_") and (path / "audio").is_dir()
    }


def validate_catalog(root: Path):
    path = root / "series" / "sound-direction-catalog.json"
    if not path.exists():
        return ["series/sound-direction-catalog.json is missing"]
    try:
        data = load_json(path)
    except Exception as exc:
        return [f"invalid sound-direction catalog JSON: {exc}"]
    errors = []
    if data.get("version") != 1:
        errors.append("sound-direction catalog version must be 1")
    entries = data.get("series")
    if not isinstance(entries, dict):
        return errors + ["sound-direction catalog series must be an object"]

    actual = real_series(root)
    configured = set(entries)
    for missing in sorted(actual - configured):
        errors.append(f"catalog missing real series {missing!r}")
    for unknown in sorted(configured - actual):
        errors.append(f"catalog contains unknown/non-audio series {unknown!r}")
    for slug, policy in sorted(entries.items()):
        if not isinstance(policy, dict):
            errors.append(f"catalog {slug}: policy must be an object")
            continue
        if policy.get("mode") not in MODES:
            errors.append(f"catalog {slug}: invalid mode")
        if policy.get("default_density") not in DENSITIES:
            errors.append(f"catalog {slug}: invalid default_density")
        if not isinstance(policy.get("goal"), str) or not policy.get("goal", "").strip():
            errors.append(f"catalog {slug}: goal is required")
    return errors


def validate_review(root: Path, programs):
    path = root / "series" / "sound-direction-review-v1.json"
    if not path.exists():
        return ["series/sound-direction-review-v1.json is missing"], {}

    try:
        data = load_json(path)
    except Exception as exc:
        return [f"invalid sound-direction review JSON: {exc}"], {}

    errors = []
    if data.get("version") != 1:
        errors.append("sound-direction review version must be 1")
    entries = data.get("entries")
    if not isinstance(entries, list):
        return errors + ["sound-direction review entries must be an array"], {}

    reviewed = {}
    for index, entry in enumerate(entries, start=1):
        prefix = f"review entry {index}"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        program_id = entry.get("id")
        if not isinstance(program_id, str) or not program_id:
            errors.append(f"{prefix}: id is required")
            continue
        if program_id in reviewed:
            errors.append(f"{prefix}: duplicate id {program_id!r}")
            continue
        reviewed[program_id] = entry
        if entry.get("density") not in DENSITIES:
            errors.append(f"{prefix}: invalid density")
        if entry.get("decision") not in DECISIONS:
            errors.append(f"{prefix}: decision must be one of {sorted(DECISIONS)}")
        if entry.get("decision") == "enhance":
            if not isinstance(entry.get("focus"), str) or not entry.get("focus", "").strip():
                errors.append(f"{prefix}: enhance requires a non-empty focus")

    real = set(real_programs(root, programs))
    configured = set(reviewed)
    for missing in sorted(real - configured):
        errors.append(f"review missing real audio program {missing!r}")
    for unknown in sorted(configured - real):
        errors.append(f"review contains unknown/showcase program {unknown!r}")
    return errors, reviewed


def validate_direction(path: Path, programs, reviewed):
    errors = []
    try:
        data = load_json(path)
    except Exception as exc:
        return [f"invalid JSON: {exc}"]

    if data.get("version") != 1:
        errors.append("version must be 1")
    program_id = data.get("id")
    if not isinstance(program_id, str) or not program_id:
        errors.append("id is required")
    if data.get("mode") not in MODES:
        errors.append(f"mode must be one of {sorted(MODES)}")
    if data.get("density") not in DENSITIES:
        errors.append(f"density must be one of {sorted(DENSITIES)}")
    if not isinstance(data.get("goal"), str) or not data.get("goal", "").strip():
        errors.append("goal is required")

    beats = data.get("beats")
    if not isinstance(beats, list):
        errors.append("beats must be an array")
        beats = []

    seen = set()
    for index, beat in enumerate(beats, start=1):
        prefix = f"beat {index}"
        if not isinstance(beat, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        beat_id = beat.get("id")
        if not isinstance(beat_id, str) or not beat_id:
            errors.append(f"{prefix}: id is required")
        elif beat_id in seen:
            errors.append(f"{prefix}: duplicate id {beat_id!r}")
        else:
            seen.add(beat_id)
        if beat.get("attention_owner") not in ATTENTION:
            errors.append(f"{prefix}: invalid attention_owner")
        if not isinstance(beat.get("purpose"), str) or not beat.get("purpose", "").strip():
            errors.append(f"{prefix}: purpose is required")
        after = beat.get("after_segment")
        if after is not None and (not isinstance(after, int) or after < 1):
            errors.append(f"{prefix}: after_segment must be >= 1")
        if beat.get("attention_owner") == "sound" and not beat.get("sound"):
            errors.append(f"{prefix}: sound owner requires a sound id")

    if data.get("density") == "none" and any(
        isinstance(beat, dict) and beat.get("attention_owner") == "sound" for beat in beats
    ):
        errors.append("density 'none' cannot contain a sound-owned beat")

    match = programs.get(program_id)
    if program_id and match is None:
        errors.append(f"no audio program found with id {program_id!r}")
    elif match:
        _, program = match
        segment_count = len(program.get("segments") or [])
        for index, beat in enumerate(beats, start=1):
            if isinstance(beat, dict) and isinstance(beat.get("after_segment"), int):
                if beat["after_segment"] > segment_count:
                    errors.append(
                        f"beat {index}: after_segment {beat['after_segment']} exceeds {segment_count} segments"
                    )

    review = reviewed.get(program_id)
    if review and review.get("density") != data.get("density"):
        errors.append(
            f"density {data.get('density')!r} disagrees with review {review.get('density')!r}"
        )
    return errors


def cmd_validate(args):
    root = Path(args.root).resolve()
    programs = audio_programs(root)
    direction_files = sorted(root.glob("series/**/direction/*.direction.json"))
    failures = 0

    catalog_errors = validate_catalog(root)
    if catalog_errors:
        failures += 1
        print("FAIL series/sound-direction-catalog.json")
        for error in catalog_errors:
            print(f"  - {error}")
    else:
        print(
            f"OK   series/sound-direction-catalog.json "
            f"({len(real_series(root))} real series calibrated)"
        )

    review_errors, reviewed = validate_review(root, programs)
    if review_errors:
        failures += 1
        print("FAIL series/sound-direction-review-v1.json")
        for error in review_errors:
            print(f"  - {error}")
    else:
        counts = {decision: 0 for decision in DECISIONS}
        for entry in reviewed.values():
            counts[entry["decision"]] += 1
        print(
            "OK   series/sound-direction-review-v1.json "
            f"({len(reviewed)}/{len(real_programs(root, programs))} real programs reviewed; "
            f"keep={counts['keep']}, direct={counts['direct']}, enhance={counts['enhance']})"
        )

    directed_ids = set()
    for path in direction_files:
        errors = validate_direction(path, programs, reviewed)
        if errors:
            failures += 1
            print(f"FAIL {path.relative_to(root)}")
            for error in errors:
                print(f"  - {error}")
        else:
            data = load_json(path)
            directed_ids.add(data["id"])
            print(f"OK   {path.relative_to(root)}")

    total = len(programs)
    directed = len(directed_ids & set(programs))
    coverage = (100.0 * directed / total) if total else 100.0
    print(
        f"Detailed Sound Direction: {len(direction_files)} sidecar(s), "
        f"{directed}/{total} audio program(s) directed ({coverage:.1f}% sidecar coverage)."
    )
    return 1 if failures else 0


def default_out(program_path: Path):
    if program_path.parent.name == "audio":
        return program_path.parent.parent / "direction" / f"{program_path.stem}.direction.json"
    return program_path.with_suffix(".direction.json")


def cmd_scaffold(args):
    program_path = Path(args.program)
    program = load_json(program_path)
    program_id = program.get("id")
    if not program_id:
        raise SystemExit("program has no id")
    out = Path(args.out) if args.out else default_out(program_path)
    if out.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {out}; use --force")
    sidecar = {
        "version": 1,
        "id": program_id,
        "mode": args.mode,
        "density": args.density,
        "goal": args.goal or "Direct the listener's attention while keeping the story primary.",
        "historical_mode": args.historical_mode,
        "constraints": DEFAULT_CONSTRAINTS,
        "characters": {},
        "beats": [],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Sound Direction v1 utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser(
        "validate", help="validate series catalog, full review coverage and detailed sidecars"
    )
    validate.add_argument("--root", default=".")
    validate.set_defaults(func=cmd_validate)

    scaffold = sub.add_parser(
        "scaffold", help="create an empty direction sidecar for an audio program"
    )
    scaffold.add_argument("program")
    scaffold.add_argument("--mode", choices=sorted(MODES), required=True)
    scaffold.add_argument("--density", choices=sorted(DENSITIES), default="light")
    scaffold.add_argument(
        "--historical-mode",
        choices=["documented", "reconstruction", "evocation-composite", "not-applicable"],
        default="documented",
    )
    scaffold.add_argument("--goal")
    scaffold.add_argument("--out")
    scaffold.add_argument("--force", action="store_true")
    scaffold.set_defaults(func=cmd_scaffold)
    return parser


def main():
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
