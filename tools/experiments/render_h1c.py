#!/usr/bin/env python3
import argparse
import asyncio
import hashlib
import json
import math
import random
from pathlib import Path

import edge_tts
import numpy as np
import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from pydub import AudioSegment

from audio_engine.voice_lab_azure import AzureSpeechLabClient, AzureSpeechLabError


def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for ch in iter(lambda:f.read(1024*1024),b""):
            h.update(ch)
    return h.hexdigest()


def key(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",",":")).encode("utf-8")
    ).hexdigest()


async def edge_render(seg, out):
    await edge_tts.Communicate(
        seg["text"], seg["voice"],
        rate=seg.get("rate","+0%"),
        pitch=seg.get("pitch","+0Hz"),
        volume=seg.get("volume","+0%"),
    ).save(str(out))


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def normalize(seg, target=-20.0):
    seg=seg.set_frame_rate(24000).set_channels(2)
    if math.isfinite(seg.dBFS):
        seg=seg.apply_gain(max(-8,min(8,target-seg.dBFS)))
    return seg


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--spec",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    cache=out/"shared-cache"; cache.mkdir(exist_ok=True)
    refs=out/"refs"; refs.mkdir(exist_ok=True)

    try:
        azure=AzureSpeechLabClient.from_env()
    except AzureSpeechLabError as exc:
        raise SystemExit(f"AZURE_CAPABILITY_PREFLIGHT_FAILED: {exc}")

    # Synthetic consent-safe reference for the already accepted Chatterbox women.
    r=spec["synthetic_references"]["vivienne"]
    ref_mp3=refs/"vivienne.mp3"; ref_wav=refs/"vivienne.wav"
    asyncio.run(edge_render({
        "text":r["text"],"voice":r["voice"],"rate":r["rate"],"pitch":r["pitch"],"volume":r["volume"]
    },ref_mp3))
    AudioSegment.from_file(ref_mp3).export(ref_wav,format="wav")

    model=ChatterboxMultilingualTTS.from_pretrained(device="cpu",t3_model="v3")

    edge_cache={}
    cb_cache={}
    azure_cache={}

    def render_raw(seg, variant_name, index):
        provider=seg["provider"]
        if provider=="edge":
            ident={
                "provider":"edge","text":seg["text"],"voice":seg["voice"],
                "rate":seg.get("rate","+0%"),"pitch":seg.get("pitch","+0Hz"),"volume":seg.get("volume","+0%")
            }
            k=key(ident)
            if k not in edge_cache:
                p=cache/f"edge-{k}.mp3"
                asyncio.run(edge_render(seg,p))
                edge_cache[k]=p
            return edge_cache[k],{"provider":"edge","cache_key":k}

        if provider=="chatterbox":
            ident={
                "provider":"chatterbox","text":seg["text"],"ref":seg["ref"],
                "exaggeration":seg.get("exaggeration",0.5),
                "cfg_weight":seg.get("cfg_weight",0.5),
                "temperature":seg.get("temperature",0.8)
            }
            k=key(ident)
            if k not in cb_cache:
                p=cache/f"cb-{k}.wav"
                seed_all(int(k[:8],16))
                wav=model.generate(
                    seg["text"],language_id="fr",audio_prompt_path=str(ref_wav),
                    exaggeration=seg.get("exaggeration",0.5),
                    cfg_weight=seg.get("cfg_weight",0.5),
                    temperature=seg.get("temperature",0.8),
                )
                ta.save(str(p),wav,model.sr)
                cb_cache[k]=p
            return cb_cache[k],{"provider":"chatterbox","cache_key":k}

        if provider=="azure":
            ident={
                "provider":"azure","text":seg["text"],"voice":seg["voice"],
                "locale":seg.get("locale","fr-FR"),"style":seg.get("style"),
                "styledegree":seg.get("styledegree"),"rate":seg.get("rate"),
                "pitch":seg.get("pitch"),"volume":seg.get("volume")
            }
            k=key(ident)
            if k not in azure_cache:
                p=cache/f"azure-{k}.mp3"
                manifest=azure.synthesize(
                    seg["text"],seg["voice"],p,
                    locale=seg.get("locale","fr-FR"),
                    style=seg.get("style"),
                    styledegree=seg.get("styledegree"),
                    rate=seg.get("rate"),
                    pitch=seg.get("pitch"),
                    volume=seg.get("volume"),
                )
                azure_cache[k]=(p,manifest)
            p,manifest=azure_cache[k]
            return p,{"provider":"azure","cache_key":k,"azure":manifest}

        raise RuntimeError(f"unsupported provider {provider}")

    reports=[]
    for variant_name,variant in spec["variants"].items():
        final=AudioSegment.empty()
        seg_reports=[]
        for i,seg in enumerate(variant["segments"],1):
            raw,meta=render_raw(seg,variant_name,i)
            audio=normalize(AudioSegment.from_file(raw))
            if "pan" in seg:
                audio=audio.pan(float(seg["pan"]))
            final += audio
            pause=int(seg.get("pause_after_ms",0))
            if pause:
                final += AudioSegment.silent(duration=pause,frame_rate=24000)
            seg_reports.append({
                "i":i,"speaker":seg["speaker"],"provider":seg["provider"],
                "text":seg["text"],"style":seg.get("style"),
                "styledegree":seg.get("styledegree"),
                "raw_sha256":sha256(raw),"audio_ms":len(audio),"pause_ms":pause,
                **meta,
            })

        target=out/f"{variant_name}.mp3"
        final.export(target,format="mp3",bitrate="128k")
        report={
            "schema_version":1,
            "variant":variant_name,
            "module":variant["module"],
            "title":variant["title"],
            "audio_duration_seconds":len(final)/1000,
            "audio_sha256":sha256(target),
            "segments":seg_reports,
            "upstream":spec["upstream"],
            "azure_region":azure.region,
        }
        rp=out/f"{variant_name}-report.json"
        rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        reports.append(report)

    summary={
        "schema_version":1,
        "source_spec":spec["id"],
        "variants":[{"variant":r["variant"],"module":r["module"],"audio_sha256":r["audio_sha256"],"duration":r["audio_duration_seconds"]} for r in reports],
        "shared_cache":{"edge":len(edge_cache),"chatterbox":len(cb_cache),"azure":len(azure_cache)},
        "azure_region":azure.region,
    }
    (out/"h1c-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
