#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
from pathlib import Path

from pydub import AudioSegment

from audio_engine.voice_lab_azure import AzureSpeechLabClient, AzureSpeechLabError


FROZEN_SCOPE = {
    "P4": {
        2: ("Sirène gauche", "Ulysse d’Ithaque."),
        4: ("Sirène gauche", "Troie."),
        6: ("Sirène gauche", "Pourquoi tu as crié ton nom."),
        8: ("Sirène gauche", "…ou être connu ?"),
        12: ("Sirène gauche", "Nous savons déjà."),
    },
    "P6": {
        2: ("Ulysse", "Non."),
        4: ("Ulysse", "Ce lit ne sort pas de cette chambre."),
        10: ("Ulysse", "Tu le savais."),
        12: ("Ulysse", "Pénélope…"),
        15: ("Ulysse", "Notre lit."),
    },
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pcm_sha256(segment):
    h = hashlib.sha256()
    h.update(str(segment.frame_rate).encode())
    h.update(b"|")
    h.update(str(segment.channels).encode())
    h.update(b"|")
    h.update(str(segment.sample_width).encode())
    h.update(b"|")
    h.update(segment.raw_data)
    return h.hexdigest()


def normalize(segment, target=-20.0):
    segment = segment.set_frame_rate(24000).set_channels(2)
    if math.isfinite(segment.dBFS):
        segment = segment.apply_gain(max(-8, min(8, target - segment.dBFS)))
    return segment


def validate_scope(module, report, replacements):
    expected = FROZEN_SCOPE[module]
    if set(replacements) != set(expected):
        raise SystemExit(
            f"{module}_SCOPE_REJECT: replacements={sorted(replacements)} "
            f"expected={sorted(expected)}"
        )

    segments = {int(s["i"]): s for s in report["segments"]}
    for i, (speaker, text) in expected.items():
        if i not in segments:
            raise SystemExit(f"{module}_BASELINE_SEGMENT_MISSING:{i}")
        base = segments[i]
        if base["speaker"] != speaker or base["text"] != text:
            raise SystemExit(
                f"{module}_BASELINE_BINDING_REJECT:{i}:"
                f"{base['speaker']!r}/{base['text']!r}"
            )
        repl = replacements[i]
        if repl["speaker"] != speaker or repl["text"] != text:
            raise SystemExit(
                f"{module}_REPLACEMENT_BINDING_REJECT:{i}:"
                f"{repl['speaker']!r}/{repl['text']!r}"
            )


def load_baseline(module_cfg, baseline_dir):
    audio_path = baseline_dir / module_cfg["audio"]
    report_path = baseline_dir / module_cfg["report"]
    if sha256(audio_path) != module_cfg["audio_sha256"]:
        raise SystemExit(f"{module_cfg['module']}_BASELINE_AUDIO_SHA_REJECT")
    if sha256(report_path) != module_cfg["report_sha256"]:
        raise SystemExit(f"{module_cfg['module']}_BASELINE_REPORT_SHA_REJECT")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report["variant"] != module_cfg["variant"]:
        raise SystemExit(f"{module_cfg['module']}_BASELINE_VARIANT_REJECT")

    audio = AudioSegment.from_file(audio_path)
    if audio.frame_rate != 24000 or audio.channels != 2:
        raise SystemExit(
            f"{module_cfg['module']}_BASELINE_FORMAT_REJECT:"
            f"{audio.frame_rate}Hz/{audio.channels}ch"
        )

    scheduled_ms = sum(
        int(s["audio_ms"]) + int(s.get("pause_ms", 0))
        for s in report["segments"]
    )
    drift_ms = len(audio) - scheduled_ms
    if abs(drift_ms) > 120:
        raise SystemExit(
            f"{module_cfg['module']}_BASELINE_TIMELINE_REJECT:"
            f"decoded={len(audio)} scheduled={scheduled_ms} drift={drift_ms}"
        )
    return audio, report, drift_ms


def render_variant(spec, variant_name, variant, baseline_dir, out, azure):
    module = variant["module"]
    module_cfg = spec["modules"][module]
    baseline, baseline_report, baseline_drift_ms = load_baseline(
        module_cfg, baseline_dir
    )
    replacements = {int(r["i"]): r for r in variant["replacements"]}
    validate_scope(module, baseline_report, replacements)

    final = AudioSegment.empty()
    cursor = 0
    segment_reports = []
    slots_dir = out / "slots"
    slots_dir.mkdir(exist_ok=True)

    for base_seg in baseline_report["segments"]:
        i = int(base_seg["i"])
        audio_ms = int(base_seg["audio_ms"])
        pause_ms = int(base_seg.get("pause_ms", 0))
        speech_start = cursor
        speech_end = speech_start + audio_ms
        slot_end = speech_end + pause_ms

        if i in replacements:
            repl = replacements[i]
            raw_path = out / "azure-raw" / f"{variant_name}-{i:02d}.mp3"
            raw_path.parent.mkdir(exist_ok=True)
            manifest = azure.synthesize(
                repl["text"],
                repl["voice"],
                raw_path,
                locale=repl.get("locale", "fr-FR"),
                style=repl.get("style"),
                styledegree=repl.get("styledegree"),
                rate=repl.get("rate"),
                pitch=repl.get("pitch"),
                volume=repl.get("volume"),
            )
            inserted = normalize(AudioSegment.from_file(raw_path))
            if "pan" in repl:
                inserted = inserted.pan(float(repl["pan"]))

            slot_path = slots_dir / f"{variant_name}-{i:02d}.wav"
            inserted.export(slot_path, format="wav")

            final += inserted
            if pause_ms:
                final += baseline[speech_end:slot_end]

            segment_reports.append(
                {
                    "i": i,
                    "speaker": base_seg["speaker"],
                    "text": base_seg["text"],
                    "source": "azure-replacement",
                    "baseline_audio_ms": audio_ms,
                    "candidate_audio_ms": len(inserted),
                    "pause_ms_preserved": pause_ms,
                    "slot_wav": str(slot_path.relative_to(out)),
                    "slot_wav_sha256": sha256(slot_path),
                    "raw_sha256": sha256(raw_path),
                    "azure": manifest,
                }
            )
        else:
            preserved = baseline[speech_start:slot_end]
            final += preserved
            segment_reports.append(
                {
                    "i": i,
                    "speaker": base_seg["speaker"],
                    "text": base_seg["text"],
                    "source": "immutable-h1b-b-decoded-slice",
                    "audio_ms": audio_ms,
                    "pause_ms": pause_ms,
                    "preserved_pcm_sha256": pcm_sha256(preserved),
                }
            )
        cursor = slot_end

    if cursor < len(baseline):
        final += baseline[cursor:]

    target = out / f"{variant_name}.mp3"
    final.export(target, format="mp3", bitrate="128k")

    report = {
        "schema_version": 2,
        "variant": variant_name,
        "module": module,
        "title": variant["title"],
        "architecture": "surgical replacement over immutable H1b-B baseline",
        "baseline": {
            "release_tag": spec["baseline_release"]["tag"],
            "target_commit": spec["baseline_release"]["target_commit"],
            "variant": module_cfg["variant"],
            "audio_sha256": module_cfg["audio_sha256"],
            "report_sha256": module_cfg["report_sha256"],
            "decoded_duration_ms": len(baseline),
            "reported_schedule_ms": cursor,
            "decode_drift_ms": baseline_drift_ms,
        },
        "frozen_replacement_indices": sorted(replacements),
        "preserved_indices": [
            int(s["i"]) for s in baseline_report["segments"]
            if int(s["i"]) not in replacements
        ],
        "audio_duration_seconds": len(final) / 1000,
        "audio_sha256": sha256(target),
        "segments": segment_reports,
        "upstream": spec["upstream"],
        "azure_region": azure.region,
        "machine_verdict": {
            "baseline_integrity": "PASS",
            "surgical_scope": "PASS",
            "text_binding": "PASS",
            "candidate_nonempty": "PASS" if len(final) > 0 else "FAIL",
            "human_gate_required": True,
        },
    }
    report_path = out / f"{variant_name}-report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--baseline-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    baseline_dir = Path(args.baseline_dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    try:
        azure = AzureSpeechLabClient.from_env()
    except AzureSpeechLabError as exc:
        raise SystemExit(f"AZURE_CAPABILITY_PREFLIGHT_FAILED: {exc}")

    reports = []
    for variant_name, variant in spec["variants"].items():
        reports.append(
            render_variant(
                spec, variant_name, variant, baseline_dir, out, azure
            )
        )

    summary = {
        "schema_version": 2,
        "source_spec": spec["id"],
        "architecture": "surgical-h1b-b-slot-replacement",
        "baseline_release": spec["baseline_release"],
        "variants": [
            {
                "variant": r["variant"],
                "module": r["module"],
                "audio_sha256": r["audio_sha256"],
                "duration": r["audio_duration_seconds"],
                "replacement_indices": r["frozen_replacement_indices"],
            }
            for r in reports
        ],
        "azure_region": azure.region,
        "human_gate": "PENDING",
    }
    (out / "h1c-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
