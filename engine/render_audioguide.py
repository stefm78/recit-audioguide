#!/usr/bin/env python3
import argparse, asyncio, json, pathlib, subprocess, tempfile
import edge_tts
import imageio_ffmpeg

AGE_ORDER={"child":0,"young_adult":1,"adult":2,"older":3}
NUMERIC_TRAITS={"energy":1.5,"authority":1.4,"warmth":1.0,"darkness":1.1,"proximity":1.0}


def load_json(path): return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))

def casting_score(target,preset):
    traits=preset['traits']; score=0.0
    gender=target.get('gender','any')
    if gender!='any' and traits.get('gender')!=gender: score+=25.0
    age=target.get('age','any')
    if age!='any': score+=7.0*abs(AGE_ORDER[age]-AGE_ORDER[traits['age']])
    for key,weight in NUMERIC_TRAITS.items():
        if key in target:
            delta=float(target[key])-float(traits[key]); score+=weight*delta*delta
    score-=2.0*len(set(target.get('tags',[])) & set(preset.get('tags',[])))
    return score

def choose_preset(target,presets):
    ranked=sorted(((casting_score(target,p),p) for p in presets),key=lambda x:(x[0],x[1]['id']))
    return ranked[0][1],ranked[:3]

def resolve_cast(guide,palette):
    presets=palette['presets']; by_id={p['id']:p for p in presets}; cast={}; resolved=[]
    for index,segment in enumerate(guide['segments'],1):
        cid=segment.get('character_id') or f'segment-{index}'; explicit=segment.get('preset')
        if explicit: preset=by_id[explicit]; alternatives=[]
        elif cid in cast: preset=cast[cid]; alternatives=[]
        else:
            preset,ranked=choose_preset(segment.get('target',{}),presets); cast[cid]=preset
            alternatives=[{'preset':p['id'],'score':round(score,3)} for score,p in ranked]
        resolved.append({**segment,'sequence':index,'resolved_preset':preset['id'],'voice':preset['voice'],'rate':preset['rate'],'pitch':preset['pitch'],'volume':preset['volume'],'casting_alternatives':alternatives})
    return resolved

async def synthesize_segment(segment,path):
    last=None
    for attempt in range(2):
        try:
            await edge_tts.Communicate(segment['text'],segment['voice'],rate=segment['rate'],pitch=segment['pitch'],volume=segment['volume']).save(str(path)); return
        except Exception as e:
            last=e
            if attempt==0: await asyncio.sleep(1.5)
    raise last

def run_ffmpeg(args): subprocess.run(args,check=True)

def silence_file(ffmpeg,directory,duration_ms,cache):
    duration_ms=int(duration_ms)
    if duration_ms<=0:return None
    if duration_ms in cache:return cache[duration_ms]
    path=directory/f'silence-{duration_ms}ms.mp3'
    run_ffmpeg([ffmpeg,'-hide_banner','-loglevel','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t',f'{duration_ms/1000:.3f}','-c:a','libmp3lame','-b:a','64k',str(path)])
    cache[duration_ms]=path; return path

async def render(guide_path,palette_path,output_root):
    guide=load_json(guide_path); palette=load_json(palette_path); resolved=resolve_cast(guide,palette)
    guide_id=guide['id']; output_dir=pathlib.Path(output_root)/guide_id; output_dir.mkdir(parents=True,exist_ok=True)
    final_path=output_dir/'guide.mp3'; ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory() as tmp:
        d=pathlib.Path(tmp); parts=[]; cache={}
        lead=silence_file(ffmpeg,d,guide.get('lead_in_ms',250),cache)
        if lead:parts.append(lead)
        for segment in resolved:
            clip=d/f"{segment['sequence']:03d}.mp3"; await synthesize_segment(segment,clip); parts.append(clip)
            pause=silence_file(ffmpeg,d,segment.get('pause_after_ms',350),cache)
            if pause:parts.append(pause)
        concat=d/'concat.txt'; concat.write_text(''.join(f"file '{p.resolve()}'\n" for p in parts),encoding='utf-8')
        run_ffmpeg([ffmpeg,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-c:a','libmp3lame','-b:a','128k','-ar','24000','-ac','1',str(final_path)])
    manifest={'guide':{'id':guide_id,'title':guide['title'],'location':guide.get('location'),'historical_note':guide.get('historical_note'),'sources':guide.get('sources',[])},'segments':resolved}
    (output_dir/'resolved-cast.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('guide'); parser.add_argument('--palette',default=str(pathlib.Path(__file__).with_name('voice-palette.json'))); parser.add_argument('--output-root',default='generated/audio'); args=parser.parse_args()
    asyncio.run(render(args.guide,args.palette,args.output_root))
if __name__=='__main__': main()
