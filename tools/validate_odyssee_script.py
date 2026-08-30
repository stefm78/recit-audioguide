#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "series" / "odyssee" / "text"
FILES = [TEXT / f"block-{x}.md" for x in "abcd"]
ATTR = "Adaptation française originale inspirée de L’Odyssée attribuée à Homère"
SEQ_RE = re.compile(r"^# S(\d{2})\s+—\s+.+$", re.M)
CUE_RE = re.compile(r"^([A-ZÉÈÀÙÂÊÎÔÛÇÏÜŒ -]+) — (.+)$")
WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿŒœ’'-]+")
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", re.I)

BLOCK_RANGES = {
    "block-a.md": (2500, 3200),
    "block-b.md": (3000, 3900),
    "block-c.md": (1800, 2500),
    "block-d.md": (3400, 4300),
}
TOTAL_RANGE = (11000, 12500)

REQUIRED = {
    "block-a.md": {"NARRATRICE", "ULYSSE", "PÉNÉLOPE", "TÉLÉMAQUE", "ATHÉNA"},
    "block-b.md": {"ULYSSE", "EURYLOQUE", "POLYPHÈME", "CIRCÉ", "ANTICLÉE"},
    "block-c.md": {"ULYSSE", "EURYLOQUE", "SIRÈNE", "ALCINOOS", "ATHÉNA"},
    "block-d.md": {"ULYSSE", "PÉNÉLOPE", "TÉLÉMAQUE", "EURYCLÉE", "EUMÉE"},
}


def spoken_lines(text):
    result = []
    errors = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if " — " not in line or line.startswith("#"):
            continue
        match = CUE_RE.fullmatch(line)
        if not match:
            errors.append(f"line {lineno}: invalid speaker cue: {line}")
        else:
            result.append((match.group(1), match.group(2)))
    return result, errors


def validate():
    errors = []
    report = {"status": "PASS", "blocks": {}, "total_spoken_words": 0}
    sequences = []

    for path in FILES:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if ATTR not in text:
            errors.append(f"{path.name}: original-adaptation attribution missing")
        if PLACEHOLDER_RE.search(text):
            errors.append(f"{path.name}: placeholder token found")

        seq = [int(x) for x in SEQ_RE.findall(text)]
        sequences.extend(seq)

        lines, cue_errors = spoken_lines(text)
        errors.extend(f"{path.name}: {e}" for e in cue_errors)
        speakers = {speaker for speaker, _ in lines}
        missing_speakers = REQUIRED[path.name] - speakers
        if missing_speakers:
            errors.append(f"{path.name}: missing required speakers: {sorted(missing_speakers)}")

        words = sum(len(WORD_RE.findall(spoken)) for _, spoken in lines)
        lo, hi = BLOCK_RANGES[path.name]
        if not lo <= words <= hi:
            errors.append(f"{path.name}: spoken words {words} outside {lo}..{hi}")
        report["blocks"][path.name] = {
            "sequences": seq,
            "spoken_words": words,
            "speakers": sorted(speakers),
        }
        report["total_spoken_words"] += words

    expected = list(range(1, 16))
    if sorted(sequences) != expected or len(sequences) != 15:
        errors.append(f"sequence coverage invalid: got {sequences}, expected S01..S15 exactly once")

    lo, hi = TOTAL_RANGE
    if not lo <= report["total_spoken_words"] <= hi:
        errors.append(
            f"total spoken words {report['total_spoken_words']} outside {lo}..{hi}"
        )

    golden_wpm = 156.5
    report["golden_reference_effective_wpm"] = golden_wpm
    report["estimated_minutes_at_golden_wpm"] = round(
        report["total_spoken_words"] / golden_wpm, 1
    )

    if errors:
        report["status"] = "FAIL"
        report["errors"] = errors
    return report


def main():
    report = validate()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
