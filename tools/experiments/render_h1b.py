#!/usr/bin/env python3
import argparse, asyncio, hashlib, json, math, random
from pathlib import Path
import edge_tts, numpy as np, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from pydub import AudioSegment

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for ch in iter(lambda:f.read(1024*1024),b""): h.update(ch)
    return h.hexdigest()

async def edge(seg,out):
    await edge_tts.Communicate(seg["text"],seg["voice"],rate=seg["rate"],pitch=seg["pitch"],volume=seg["volume"]).save(str(out))

def norm(seg,target=-20.0):
    seg=seg.set_frame_rate(24000).set_channels(2)
    if math.isfinite(seg.dBFS):
        seg=seg.apply_gain(max(-8,min(8,target-seg.dBFS)))
    return seg

def seed_all(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)

def dark_air(ms,seed,target_dbfs=-43.0):
    rng=np.random.default_rng(seed)
    x=np.clip(rng.normal(0,0.18,int(24000*ms/1000)), -1,1)
    pcm=(x*32767).astype(np.int16).tobytes()
    a=AudioSegment(data=pcm,sample_width=2,frame_rate=24000,channels=1).set_channels(2)
    a=a.low_pass_filter(180).high_pass_filter(35)
    if math.isfinite(a.dBFS): a=a.apply_gain(target_dbfs-a.dBFS)
    return a.fade_in(1200).fade_out(1600)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--spec",required=True); ap.add_argument("--variant",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    spec=json.loads(Path(args.spec).read_text(encoding="utf-8")); v=spec["variants"][args.variant]
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True); work=out/"segments"; work.mkdir(exist_ok=True)
    refs=out/"refs"; refs.mkdir(exist_ok=True)

    # Synthetic, consent-safe reference voices for Chatterbox conditioning.
    for name,r in spec["synthetic_references"].items():
        mp3=refs/f"{name}.mp3"; wav=refs/f"{name}.wav"
        asyncio.run(edge({"text":r["text"],"voice":r["voice"],"rate":r["rate"],"pitch":r["pitch"],"volume":r["volume"]},mp3))
        AudioSegment.from_file(mp3).export(wav,format="wav")

    need_cb=any(s["provider"]=="chatterbox" for s in v["segments"])
    model=ChatterboxMultilingualTTS.from_pretrained(device="cpu",t3_model="v3") if need_cb else None

    final=AudioSegment.empty()
    report=[]
    for i,s in enumerate(v["segments"],1):
        if s["provider"]=="edge":
            raw=work/f"{i:02d}-edge.mp3"; asyncio.run(edge(s,raw))
        else:
            raw=work/f"{i:02d}-cb.wav"
            seed_all(int(v["seed"])*100+i)
            wav=model.generate(
                s["text"], language_id="fr", audio_prompt_path=str(refs/f'{s["ref"]}.wav'),
                exaggeration=s.get("exaggeration",0.5), cfg_weight=s.get("cfg_weight",0.5),
                temperature=s.get("temperature",0.8)
            )
            ta.save(str(raw),wav,model.sr)
        a=norm(AudioSegment.from_file(raw))
        if "pan" in s: a=a.pan(float(s["pan"]))
        if s.get("effect")=="near_reflection":
            ext=a+AudioSegment.silent(duration=75,frame_rate=24000)
            ext=ext.overlay((AudioSegment.silent(duration=65,frame_rate=24000)+a.apply_gain(-29)),position=0)
            a=ext
        final += a
        pause=int(s.get("pause_after_ms",0))
        if pause: final+=AudioSegment.silent(duration=pause,frame_rate=24000)
        report.append({"i":i,"speaker":s["speaker"],"provider":s["provider"],"text":s["text"],"raw_sha256":sha256(raw),"audio_ms":len(a),"pause_ms":pause})

    bed=v.get("bed")
    if bed and bed.get("type")=="dark_air":
        final=dark_air(len(final),int(v["seed"]),float(bed.get("target_dbfs",-43))).overlay(final)

    target=out/f'{args.variant}.mp3'; final.export(target,format="mp3",bitrate="128k")
    metadata={"schema_version":1,"variant":args.variant,"module":v["module"],"title":v["title"],"seed":v["seed"],"audio_duration_seconds":len(final)/1000,"audio_sha256":sha256(target),"segments":report,"upstream":spec["upstream"]}
    rp=out/f'{args.variant}-report.json'; rp.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(metadata,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
