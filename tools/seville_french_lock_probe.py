#!/usr/bin/env python3
"""Build a bounded Seville French-lock listening candidate.

This tool never edits published Seville audio specifications. It inventories the
source specs, extracts two representative source passages, renders the current
multilingual configuration and a bounded monolingual French-lock candidate, and
writes provenance for a human listening gate.

Automatic checks here prove only configuration/text/provenance invariants. They
are not evidence that the rendered audio is linguistically correct; the audio
verdict remains human/device-owned.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASELINE_COMMIT = "00764713073ed754f713fc5c86b82f1b1537abbe"
ENGINE_REF = "3392d4f22f0a9b054a05b5c05a7856985c0ab030"
SERIES = "seville-discovery"
BASELINE_VOICE = "fr-FR-RemyMultilingualNeural"
LOCK_VOICE = "fr-FR-HenriNeural"
RATE = "+8%"
PITCH = "+14Hz"
VOLUME = "+5%"

SPANISH_PROPER_SURFACE_MARKERS = (
    "Puerta ", "Patio ", "Plaza ", "Calle ", "Casa ", "Real Alcázar",
    "Salón ", "Baños ", "Galería ", "Palacio ", "Iglesia ", "Archivo ",
    "Hospital ", "Mercado ", "Torre ", "Jardines ", "Setas ",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_specs(repo: Path) -> list[Path]:
    return sorted((repo / "series" / SERIES / "audio").glob("*.json"))


def proper_surface_hits(text: str) -> list[str]:
    return [marker.strip() for marker in SPANISH_PROPER_SURFACE_MARKERS if marker in text]


def build_inventory(repo: Path) -> dict:
    programs = []
    total_segments = 0
    for path in source_specs(repo):
        data = load_json(path)
        segments = []
        for idx, segment in enumerate(data.get("segments", []), start=1):
            text = segment.get("text", "")
            segments.append(
                {
                    "sequence": idx,
                    "text": text,
                    "text_sha256": sha256_text(text),
                    "proper_name_surface_markers": proper_surface_hits(text),
                }
            )
        total_segments += len(segments)
        programs.append(
            {
                "path": str(path.relative_to(repo)).replace("\\", "/"),
                "id": data.get("id"),
                "title": data.get("title"),
                "language": data.get("language"),
                "profile": data.get("profile"),
                "segment_count": len(segments),
                "source_sha256": sha256_file(path),
                "segments": segments,
            }
        )
    return {
        "schema": "seville.french-lock.source-inventory.v1",
        "baseline_commit": BASELINE_COMMIT,
        "series": SERIES,
        "program_count": len(programs),
        "segment_count": total_segments,
        "programs": programs,
        "interpretation": {
            "proper_name_surface_markers": (
                "Inventory aid only. These markers identify Spanish-looking proper-name surfaces; "
                "they do not classify spoken language and are not audio evidence."
            ),
            "audio_language_proof": "HUMAN_LISTENING_REQUIRED",
        },
    }


def first_segment_containing(program: dict, needle: str) -> tuple[int, dict]:
    for idx, segment in enumerate(program["segments"], start=1):
        if needle in segment.get("text", ""):
            return idx, segment
    raise RuntimeError(f"No segment contains required probe marker: {needle!r}")


def choose_control_segment(program: dict) -> tuple[int, dict]:
    candidates = []
    for idx, segment in enumerate(program["segments"], start=1):
        text = segment.get("text", "")
        if len(text) < 180:
            continue
        candidates.append((len(proper_surface_hits(text)), idx, segment))
    if not candidates:
        raise RuntimeError("No suitable control segment found")
    _, idx, segment = min(candidates, key=lambda item: (item[0], item[1]))
    return idx, segment


def clone_segment(segment: dict, *, french_lock: bool) -> dict:
    cloned = copy.deepcopy(segment)
    if french_lock:
        # Remove casting selectors so synthesis identity is explicit and bounded.
        cloned.pop("preset", None)
        cloned.pop("target", None)
        cloned["voice"] = LOCK_VOICE
        cloned["rate"] = RATE
        cloned["pitch"] = PITCH
        cloned["volume"] = VOLUME
    return cloned


def minimal_program(
    source: dict,
    *,
    program_id: str,
    title: str,
    selected: list[dict],
    french_lock: bool,
) -> dict:
    return {
        "schema_version": 1,
        "id": program_id,
        "title": title,
        "language": "fr-FR",
        "profile": "speech",
        "segments": [clone_segment(segment, french_lock=french_lock) for segment in selected],
    }


def text_identity(program_a: dict, program_b: dict) -> bool:
    a = [segment["text"] for segment in program_a["segments"]]
    b = [segment["text"] for segment in program_b["segments"]]
    return a == b


def render(program_path: Path, output_root: Path) -> Path:
    subprocess.run(
        ["audio-engine", "render", str(program_path), "--out", str(output_root)],
        check=True,
    )
    program = load_json(program_path)
    audio = output_root / program["id"] / "audio.mp3"
    if not audio.is_file() or audio.stat().st_size <= 0:
        raise RuntimeError(f"Renderer produced no audio for {program['id']}")
    return audio


def render_manifest(program_path: Path, output_root: Path) -> dict:
    program = load_json(program_path)
    return load_json(output_root / program["id"] / "manifest.json")


def transcript(program_path: Path, output_root: Path) -> dict:
    program = load_json(program_path)
    return load_json(output_root / program["id"] / "transcript.json")


def resolved_synthesis(transcript_data: dict) -> list[dict]:
    rows = []
    for segment in transcript_data.get("segments", []):
        rows.append(
            {
                "sequence": segment.get("sequence"),
                "voice": segment.get("voice"),
                "resolved_preset": segment.get("resolved_preset"),
                "rate": segment.get("rate", "+0%"),
                "pitch": segment.get("pitch", "+0Hz"),
                "volume": segment.get("volume", "+0%"),
                "text_sha256": sha256_text(segment.get("text", "")),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out", default="review/seville-french-lock-candidate")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    out = (repo / args.out).resolve()
    build = repo / "build" / "seville-french-lock-probe"
    shutil.rmtree(build, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)
    (build / "programs").mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    inventory = build_inventory(repo)
    if inventory["program_count"] != 28:
        raise RuntimeError(f"Expected 28 Seville specs, got {inventory['program_count']}")
    bad_languages = [p["id"] for p in inventory["programs"] if p["language"] != "fr-FR"]
    if bad_languages:
        raise RuntimeError(f"Seville specs not declared fr-FR: {bad_languages}")

    ep02_path = repo / "series" / SERIES / "audio" / "seville-discovery-ep02.json"
    g03_path = repo / "series" / SERIES / "audio" / "seville-discovery-g03.json"
    ep02 = load_json(ep02_path)
    g03 = load_json(g03_path)

    seq_a, seg_a = first_segment_containing(ep02, "Puerta del León")
    seq_b, seg_b = first_segment_containing(ep02, "Patio de las Doncellas")
    ctrl_seq, ctrl_seg = choose_control_segment(g03)

    cases = {
        "name-heavy": {
            "source": ep02_path,
            "source_program": ep02,
            "source_sequences": [seq_a, seq_b],
            "segments": [seg_a, seg_b],
        },
        "control": {
            "source": g03_path,
            "source_program": g03,
            "source_sequences": [ctrl_seq],
            "segments": [ctrl_seg],
        },
    }

    provenance_cases = {}
    for case_name, case in cases.items():
        source_path = case["source"]
        source_program = case["source_program"]
        selected = case["segments"]
        variants = {}
        programs = {}

        for variant, french_lock in (("old", False), ("french-lock", True)):
            program_id = f"seville-french-lock-{case_name}-{variant}"
            program = minimal_program(
                source_program,
                program_id=program_id,
                title=f"Séville French-lock probe — {case_name} — {variant}",
                selected=selected,
                french_lock=french_lock,
            )
            program_path = build / "programs" / f"{program_id}.json"
            program_path.write_text(json.dumps(program, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            programs[variant] = program

            render_root = build / "renders" / case_name / variant
            audio = render(program_path, render_root)
            manifest = render_manifest(program_path, render_root)
            tx = transcript(program_path, render_root)
            target_audio = out / f"{case_name}-{variant}.mp3"
            shutil.copy2(audio, target_audio)
            variants[variant] = {
                "program_id": program_id,
                "program_sha256": sha256_file(program_path),
                "audio_file": target_audio.name,
                "audio_sha256": sha256_file(target_audio),
                "audio_bytes": target_audio.stat().st_size,
                "duration_seconds": manifest.get("audio", {}).get("duration_seconds"),
                "engine_version": manifest.get("engine_version"),
                "engine_code_sha256": manifest.get("engine_code_sha256"),
                "provider": manifest.get("provider"),
                "resolved_synthesis": resolved_synthesis(tx),
            }

        if not text_identity(programs["old"], programs["french-lock"]):
            raise RuntimeError(f"Text identity failed for {case_name}")

        old_resolved = variants["old"]["resolved_synthesis"]
        lock_resolved = variants["french-lock"]["resolved_synthesis"]
        if any(row["voice"] != BASELINE_VOICE for row in old_resolved):
            raise RuntimeError(f"Old probe did not resolve to {BASELINE_VOICE}: {old_resolved}")
        if any(row["voice"] != LOCK_VOICE for row in lock_resolved):
            raise RuntimeError(f"French-lock probe did not resolve to {LOCK_VOICE}: {lock_resolved}")
        if "Multilingual" in LOCK_VOICE or not LOCK_VOICE.startswith("fr-FR-"):
            raise RuntimeError("French-lock voice contract is not a native fr-FR voice")

        provenance_cases[case_name] = {
            "source_path": str(source_path.relative_to(repo)).replace("\\", "/"),
            "source_sha256": sha256_file(source_path),
            "source_sequences": case["source_sequences"],
            "text_sha256": [sha256_text(segment["text"]) for segment in selected],
            "text_identical_between_variants": True,
            "old": variants["old"],
            "french_lock": variants["french-lock"],
        }

    provenance = {
        "schema": "seville.french-lock.listening-candidate.v1",
        "status": "HUMAN_LISTENING_GATE",
        "published_replacement": False,
        "field_build_published": False,
        "android_field_latest_modified": False,
        "baseline_commit": BASELINE_COMMIT,
        "engine_ref": ENGINE_REF,
        "series": SERIES,
        "hypothesis": (
            "The current narrator voice is multilingual and may auto-detect Spanish around Spanish proper names. "
            "The Edge consumer endpoint in use cannot carry the provider-documented nested <lang> lock."
        ),
        "candidate_strategy": (
            "Bounded Seville-only causal probe: preserve source text and expressive controls but replace "
            "the multilingual narrator with an existing native French Edge voice to remove multilingual auto-detection."
        ),
        "baseline_synthesis": {
            "voice": BASELINE_VOICE,
            "rate": RATE,
            "pitch": PITCH,
            "volume": VOLUME,
        },
        "french_lock_synthesis": {
            "voice": LOCK_VOICE,
            "rate": RATE,
            "pitch": PITCH,
            "volume": VOLUME,
        },
        "automatic_oracle_scope": (
            "CI verifies exact text identity, declared fr-FR sources, selected voice class, render success and provenance. "
            "It does NOT prove the spoken language of audio."
        ),
        "human_acceptance": [
            "French narration remains continuous and natural.",
            "Spanish proper names may retain natural Spanish pronunciation.",
            "No narrative phrase switches into Spanish.",
            "No unacceptable degradation of voice, rhythm or intelligibility.",
        ],
        "cases": provenance_cases,
    }

    (out / "source-inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Séville — French-lock listening candidate",
        "",
        "**Status:** HUMAN_LISTENING_GATE — candidate only; no published audio or FIELD build replaced.",
        "",
        f"- Product baseline: `{BASELINE_COMMIT}`",
        f"- Audio-engine pin: `{ENGINE_REF}`",
        f"- Old voice: `{BASELINE_VOICE}` @ `{RATE}`, `{PITCH}`, `{VOLUME}`",
        f"- French-lock candidate: `{LOCK_VOICE}` @ `{RATE}`, `{PITCH}`, `{VOLUME}`",
        "- Text is byte-identical at the Unicode-string level between A/B probe programs (same UTF-8 text SHA-256).",
        "- Automatic checks are configuration/provenance checks only, not proof of spoken language.",
        "",
        "## Listen",
        "",
        "1. `name-heavy-old.mp3` then `name-heavy-french-lock.mp3` — focus on Puerta del León / Patio de las Doncellas and whether surrounding French stays French.",
        "2. `control-old.mp3` then `control-french-lock.mp3` — focus on timbre, rhythm and intelligibility cost when Spanish-name pressure is low.",
        "",
        "See `provenance.json` for source paths, exact segment sequences, text hashes, render engine identity and audio hashes.",
    ]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"status": "HUMAN_LISTENING_GATE", "out": str(out), "cases": list(cases)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
