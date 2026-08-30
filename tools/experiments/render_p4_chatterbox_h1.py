#!/usr/bin/env python3
import argparse
import asyncio
import hashlib
import json
import math
import random
import time
from pathlib import Path

import edge_tts
import numpy as np
import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from pydub import AudioSegment


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalized_segment(path: Path, target_dbfs: float = -20.0) -> AudioSegment:
    seg = AudioSegment.from_file(path).set_frame_rate(24000).set_channels(1)
    if math.isfinite(seg.dBFS):
        gain = max(-8.0, min(8.0, target_dbfs - seg.dBFS))
        seg = seg.apply_gain(gain)
    return seg


async def synth_edge(seg: dict, out: Path) -> None:
    comm = edge_tts.Communicate(
        seg["text"],
        seg["voice"],
        rate=seg["rate"],
        pitch=seg["pitch"],
        volume=seg["volume"],
    )
    await comm.save(str(out))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--variant", choices=["a", "b"], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    variant = spec["variants"][args.variant]
    seed = int(variant["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / "segments"
    work.mkdir(exist_ok=True)

    t0 = time.monotonic()
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu", t3_model="v3")
    model_loaded = time.monotonic()

    final = AudioSegment.empty()
    segment_reports = []

    for i, seg in enumerate(spec["segments"], start=1):
        provider = seg["provider"]
        started = time.monotonic()
        if provider == "edge":
            raw = work / f"{i:02d}-edge.mp3"
            asyncio.run(synth_edge(seg, raw))
        elif provider == "chatterbox":
            raw = work / f"{i:02d}-chatterbox.wav"
            wav = model.generate(
                seg["text"],
                language_id="fr",
                exaggeration=variant["exaggeration"],
                cfg_weight=variant["cfg_weight"],
                temperature=variant["temperature"],
            )
            ta.save(str(raw), wav, model.sr)
        else:
            raise ValueError(provider)

        rendered = time.monotonic()
        audio = normalized_segment(raw)
        final += audio
        pause = int(seg.get("pause_after_ms", 0))
        if pause:
            final += AudioSegment.silent(duration=pause, frame_rate=24000)

        segment_reports.append({
            "index": i,
            "speaker": seg["speaker"],
            "provider": provider,
            "text": seg["text"],
            "render_seconds": rendered - started,
            "audio_duration_ms": len(audio),
            "pause_after_ms": pause,
            "raw_sha256": sha256(raw),
        })

    output = out_dir / f"p4-{args.variant}.mp3"
    final.export(output, format="mp3", bitrate="128k")
    done = time.monotonic()

    report = {
        "schema_version": 1,
        "id": spec["id"],
        "variant": args.variant,
        "variant_params": variant,
        "seed": seed,
        "upstream": spec["upstream"],
        "edge_tts_version": getattr(edge_tts, "__version__", "unknown"),
        "model_load_seconds": model_loaded - t0,
        "total_seconds": done - t0,
        "audio_duration_seconds": len(final) / 1000.0,
        "audio_sha256": sha256(output),
        "segments": segment_reports,
    }
    report_path = out_dir / f"p4-{args.variant}-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
