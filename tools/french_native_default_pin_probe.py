#!/usr/bin/env python3
"""Cross-project qualification for the native French narration default.

This probe compares the currently pinned Audio Engine against the candidate
engine that makes fr-FR-HenriNeural the standard French narrator. It never
changes product engine pins, published audio, Pages or FIELD artifacts.

Automatic evidence proves source identity, resolved casting identity and render
provenance. Perceptual acceptance remains a human listening gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASELINE_COMMIT = "de0f9cbe603c0dca4e1fc35fcf0e320b4639b00f"
OLD_ENGINE_REF = "3392d4f22f0a9b054a05b5c05a7856985c0ab030"
NEW_ENGINE_REF = "2fc024ee41984e2d9eaa454cf4edeeb3e63c741c"
OLD_VOICE = "fr-FR-RemyMultilingualNeural"
NEW_VOICE = "fr-FR-HenriNeural"
NARRATOR_PRESET = "narrateur-vif"

CASE_DEFS = {
    "seville": {
        "path": "series/seville-discovery/audio/seville-discovery-ep02.json",
        "selectors": [("contains", "Puerta del León"), ("contains", "Patio de las Doncellas")],
        "listen_for": "French continuity around Puerta del León / Patio de las Doncellas; natural Spanish proper-name pronunciation is allowed.",
    },
    "orleans": {
        "path": "series/orleans/audio/orleans-ep01.json",
        "selectors": [("sequence", 1), ("sequence", 9)],
        "listen_for": "Narrator timbre, rhythm and French naturalness; pay attention to Orléans, Charles VII, Reims and Jeanne.",
    },
    "kernel-handover": {
        "path": "series/kernel-handover/audio/kernel-handover-explainer.json",
        "selectors": [("sequence", 1), ("contains", "City Guide Séville")],
        "listen_for": "Modern/technical French, English loan words such as kernel/handover/City Guide, and overall intelligibility.",
    },
}

ODYSSEE_CONTROL = "series/odyssee/audio/odyssee-probe-p1.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def select_segments(program: dict, selectors: list[tuple[str, object]]) -> tuple[list[int], list[dict]]:
    chosen = []
    sequences = []
    for mode, value in selectors:
        match = None
        if mode == "sequence":
            idx = int(value)
            if idx < 1 or idx > len(program.get("segments", [])):
                raise RuntimeError(f"Sequence {idx} outside program {program.get('id')}")
            match = (idx, program["segments"][idx - 1])
        elif mode == "contains":
            for idx, segment in enumerate(program.get("segments", []), start=1):
                if str(value) in segment.get("text", ""):
                    match = (idx, segment)
                    break
        else:
            raise RuntimeError(f"Unknown selector mode: {mode}")
        if match is None:
            raise RuntimeError(f"Selector {mode}={value!r} not found in {program.get('id')}")
        sequences.append(match[0])
        chosen.append(match[1])
    return sequences, chosen


def minimal_program(source: dict, case_name: str, segments: list[dict]) -> dict:
    return {
        "schema_version": 1,
        "id": f"french-native-default-{case_name}",
        "title": f"French native default qualification — {case_name}",
        "language": source.get("language", "fr-FR"),
        "profile": source.get("profile", "speech"),
        "segments": segments,
    }


def render(engine_bin: Path, program_path: Path, out_root: Path) -> tuple[Path, dict, dict]:
    subprocess.run(
        [str(engine_bin), "render", str(program_path), "--out", str(out_root)],
        check=True,
    )
    program = load_json(program_path)
    program_dir = out_root / program["id"]
    audio = program_dir / "audio.mp3"
    if not audio.is_file() or audio.stat().st_size <= 0:
        raise RuntimeError(f"No rendered audio for {program['id']} with {engine_bin}")
    manifest = load_json(program_dir / "manifest.json")
    transcript = load_json(program_dir / "transcript.json")
    return audio, manifest, transcript


def resolved_rows(transcript: dict) -> list[dict]:
    rows = []
    for seg in transcript.get("segments", []):
        rows.append(
            {
                "sequence": seg.get("sequence"),
                "voice": seg.get("voice"),
                "resolved_preset": seg.get("resolved_preset"),
                "rate": seg.get("rate", "+0%"),
                "pitch": seg.get("pitch", "+0Hz"),
                "volume": seg.get("volume", "+0%"),
                "text_sha256": sha256_text(seg.get("text", "")),
            }
        )
    return rows


def inventory(repo: Path) -> dict:
    programs = []
    totals = {
        "programs_with_segments": 0,
        "fr_fr_programs": 0,
        "segments": 0,
        "narrateur_vif_segments": 0,
        "explicit_voice_segments": 0,
        "explicit_multilingual_voice_segments": 0,
        "other_preset_segments": 0,
        "target_segments": 0,
    }
    impacted_paths = []
    explicit_multilingual = []
    for path in sorted((repo / "series").glob("**/*.json")):
        try:
            data = load_json(path)
        except Exception:
            continue
        if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
            continue
        rel = str(path.relative_to(repo)).replace("\\", "/")
        language = data.get("language")
        counts = {k: 0 for k in (
            "segments", "narrateur_vif", "explicit_voice", "explicit_multilingual_voice", "other_preset", "target"
        )}
        for idx, seg in enumerate(data["segments"], start=1):
            counts["segments"] += 1
            totals["segments"] += 1
            preset = seg.get("preset")
            voice = seg.get("voice")
            target = seg.get("target")
            if preset == NARRATOR_PRESET:
                counts["narrateur_vif"] += 1
                totals["narrateur_vif_segments"] += 1
            elif preset:
                counts["other_preset"] += 1
                totals["other_preset_segments"] += 1
            if voice:
                counts["explicit_voice"] += 1
                totals["explicit_voice_segments"] += 1
                if "Multilingual" in voice:
                    counts["explicit_multilingual_voice"] += 1
                    totals["explicit_multilingual_voice_segments"] += 1
                    explicit_multilingual.append({"path": rel, "sequence": idx, "voice": voice})
            if target is not None:
                counts["target"] += 1
                totals["target_segments"] += 1
        totals["programs_with_segments"] += 1
        if language == "fr-FR":
            totals["fr_fr_programs"] += 1
        if language == "fr-FR" and counts["narrateur_vif"]:
            impacted_paths.append(rel)
        programs.append({
            "path": rel,
            "id": data.get("id"),
            "language": language,
            **counts,
        })
    return {
        "schema": "recit.french-native-default.inventory.v1",
        "baseline_commit": BASELINE_COMMIT,
        "old_engine_ref": OLD_ENGINE_REF,
        "new_engine_ref": NEW_ENGINE_REF,
        "totals": totals,
        "narrateur_vif_impacted_paths": impacted_paths,
        "explicit_multilingual_voice_exceptions": explicit_multilingual,
        "programs": programs,
        "interpretation": {
            "narrateur_vif": "Will move from Remy Multilingual to native Henri when the consumer pin is promoted.",
            "explicit_voice": "Not silently recast by the new default; remains an explicit casting decision.",
            "explicit_multilingual_voice": "Potential French-lock exception to review separately if the product policy later forbids multilingual voices entirely.",
        },
    }


def odyssee_control(repo: Path) -> dict:
    path = repo / ODYSSEE_CONTROL
    data = load_json(path)
    rows = []
    for idx, seg in enumerate(data.get("segments", []), start=1):
        if not seg.get("voice"):
            continue
        rows.append({
            "sequence": idx,
            "character_id": seg.get("character_id"),
            "speaker": seg.get("speaker"),
            "voice": seg.get("voice"),
            "text_sha256": sha256_text(seg.get("text", "")),
        })
    return {
        "source_path": ODYSSEE_CONTROL,
        "source_sha256": sha256_file(path),
        "explicit_cast": rows,
        "expected_default_effect": "NONE",
        "reason": "Every sampled Odyssée character carries an explicit provider voice; the French default must not silently recast it.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--old-engine-bin", required=True)
    parser.add_argument("--new-engine-bin", required=True)
    parser.add_argument("--out", default="review/french-native-default-pin-candidate")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    old_bin = Path(args.old_engine_bin).resolve()
    new_bin = Path(args.new_engine_bin).resolve()
    out = (repo / args.out).resolve()
    build = repo / "build" / "french-native-default-pin-probe"
    shutil.rmtree(build, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)
    (build / "programs").mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    inv = inventory(repo)
    case_results = {}
    for case_name, case_def in CASE_DEFS.items():
        source_path = repo / case_def["path"]
        source = load_json(source_path)
        if source.get("language") != "fr-FR":
            raise RuntimeError(f"Representative source is not fr-FR: {case_def['path']}")
        sequences, selected = select_segments(source, case_def["selectors"])
        if any(seg.get("preset") != NARRATOR_PRESET for seg in selected):
            raise RuntimeError(f"Representative case {case_name} is not pure {NARRATOR_PRESET}")

        program = minimal_program(source, case_name, selected)
        program_path = build / "programs" / f"{case_name}.json"
        program_path.write_text(json.dumps(program, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        text_hashes = [sha256_text(seg.get("text", "")) for seg in selected]

        variants = {}
        for label, engine_bin, expected_voice in (
            ("old", old_bin, OLD_VOICE),
            ("native-fr", new_bin, NEW_VOICE),
        ):
            render_root = build / "renders" / case_name / label
            audio, manifest, transcript = render(engine_bin, program_path, render_root)
            rows = resolved_rows(transcript)
            if not rows or any(row["voice"] != expected_voice for row in rows):
                raise RuntimeError(
                    f"{case_name}/{label} voice mismatch: expected {expected_voice}, got {rows}"
                )
            if [row["text_sha256"] for row in rows] != text_hashes:
                raise RuntimeError(f"{case_name}/{label} text identity mismatch")
            target = out / f"{case_name}-{label}.mp3"
            shutil.copy2(audio, target)
            variants[label] = {
                "engine_ref": OLD_ENGINE_REF if label == "old" else NEW_ENGINE_REF,
                "engine_version": manifest.get("engine_version"),
                "engine_code_sha256": manifest.get("engine_code_sha256"),
                "provider": manifest.get("provider"),
                "audio_file": target.name,
                "audio_sha256": sha256_file(target),
                "audio_bytes": target.stat().st_size,
                "duration_seconds": manifest.get("audio", {}).get("duration_seconds"),
                "resolved_synthesis": rows,
            }

        case_results[case_name] = {
            "source_path": case_def["path"],
            "source_sha256": sha256_file(source_path),
            "source_sequences": sequences,
            "program_sha256": sha256_file(program_path),
            "text_sha256": text_hashes,
            "text_identical_between_variants": True,
            "listen_for": case_def["listen_for"],
            "old": variants["old"],
            "native_fr": variants["native-fr"],
        }

    provenance = {
        "schema": "recit.french-native-default.pin-candidate.v1",
        "status": "HUMAN_CROSS_PROJECT_LISTENING_GATE",
        "published_replacement": False,
        "consumer_pin_modified": False,
        "field_build_published": False,
        "pages_published": False,
        "android_field_latest_modified": False,
        "baseline_commit": BASELINE_COMMIT,
        "old_engine_ref": OLD_ENGINE_REF,
        "new_engine_ref": NEW_ENGINE_REF,
        "old_default_voice": OLD_VOICE,
        "new_default_voice": NEW_VOICE,
        "cases": case_results,
        "explicit_cast_control": odyssee_control(repo),
        "automatic_oracle_scope": (
            "CI proves source/text identity, exact engine refs, resolved voice identity, render success and explicit-cast inventory. "
            "It does not replace human listening for timbre, rhythm, pronunciation or intelligibility."
        ),
    }

    (out / "inventory.json").write_text(json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# French native default — cross-project consumer qualification",
        "",
        "**Status:** HUMAN_CROSS_PROJECT_LISTENING_GATE. Candidate only; no product pin, Pages or FIELD publication changed.",
        "",
        f"- Récit baseline: `{BASELINE_COMMIT}`",
        f"- Current engine pin: `{OLD_ENGINE_REF}`",
        f"- Candidate engine: `{NEW_ENGINE_REF}`",
        f"- Old default narrator: `{OLD_VOICE}`",
        f"- Candidate native French narrator: `{NEW_VOICE}`",
        "- A/B source text is identical; only the engine/preset voice resolution changes.",
        "",
        "## Listening order",
        "",
    ]
    for name, result in case_results.items():
        lines.append(
            f"- `{name}-old.mp3` -> `{name}-native-fr.mp3`: {result['listen_for']}"
        )
    lines += [
        "",
        "## Explicit-cast control",
        "",
        "Odyssée P1 is inventoried as an explicit-cast control. Its explicit voices are not silently recast by this default policy.",
        "Explicit multilingual French voices are listed in `inventory.json` as exceptions for any future stricter 'no multilingual French voice' policy.",
        "",
        "See `provenance.json` for exact source sequences, text hashes, engine identities and audio hashes.",
    ]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": provenance["status"], "cases": list(case_results), "totals": inv["totals"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
