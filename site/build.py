#!/usr/bin/env python3
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / 'series'
WEB = ROOT / 'web'
DIST = ROOT / 'dist'

BLOCK = []
WARN = []
VALID_TYPES = {'story','visit','route'}


def load_manifest(path: Path):
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        BLOCK.append(f'{path}: JSON invalide ({e})'); return None
    slug=path.parent.name
    data.setdefault('slug', slug)
    for field in ('slug','type','title','episodes'):
        if not data.get(field): BLOCK.append(f'{path}: champ obligatoire manquant: {field}')
    if data.get('type') not in VALID_TYPES: BLOCK.append(f'{path}: type invalide: {data.get("type")}')
    ids=set()
    for i,e in enumerate(data.get('episodes') or [],1):
        if not e.get('id') or not e.get('title'):
            BLOCK.append(f'{path}: épisode {i} sans id ou titre'); continue
        if e['id'] in ids: BLOCK.append(f'{path}: id épisode dupliqué {e["id"]}')
        ids.add(e['id'])
        if not e.get('audio_url'): WARN.append(f'{slug}/{e["id"]}: audio absent')
        if not e.get('summary'): WARN.append(f'{slug}/{e["id"]}: résumé absent')
        if data.get('type')=='route' and not e.get('launch'): WARN.append(f'{slug}/{e["id"]}: repère de lancement absent')
        for j,extra in enumerate(e.get('extras') or [],1):
            extra_id=extra.get('id')
            if extra_id:
                if extra_id in ids: BLOCK.append(f'{path}: id audio dupliqué {extra_id}')
                ids.add(extra_id)
            elif not extra.get('audio_url'):
                WARN.append(f'{slug}/{e["id"]}/extra-{j}: audio absent')
    return data


def generated_asset(directory: Path, *names):
    for name in names:
        if (directory/name).exists(): return name
    return None


def publish_generated_audio(item):
    item_id=item.get('id')
    if not item_id:
        return
    generated=ROOT/'generated'/'audio'/item_id
    audio_name=generated_asset(generated,'audio.mp3','guide.mp3')
    if not audio_name:
        return
    target=DIST/'audio'/item_id
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(generated,target,dirs_exist_ok=True)
    item['audio_url']=f"../../audio/{item_id}/{audio_name}"
    transcript_name=generated_asset(generated,'transcript.json','resolved-cast.json')
    if transcript_name:
        item['transcript_url']=f"../../audio/{item_id}/{transcript_name}"
    if (generated/'manifest.json').exists():
        item['audio_manifest_url']=f"../../audio/{item_id}/manifest.json"


def main():
    manifests=[]
    for p in sorted(SERIES.glob('*/series.json')):
        m=load_manifest(p)
        if m: manifests.append(m)
    if BLOCK:
        report={'status':'blocked','blocking':BLOCK,'warnings':WARN}
        (ROOT/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print('\n'.join('BLOCK: '+x for x in BLOCK),file=sys.stderr)
        return 2
    if DIST.exists(): shutil.rmtree(DIST)
    (DIST/'assets').mkdir(parents=True)
    (DIST/'s').mkdir()
    (DIST/'data').mkdir()
    shutil.copy2(WEB/'index.html',DIST/'index.html')
    for name in ('styles.css','home.js','app.js'): shutil.copy2(WEB/name,DIST/'assets'/name)
    tpl=(WEB/'series.html').read_text(encoding='utf-8')
    catalog=[]
    for m in manifests:
        slug=m['slug']
        out=DIST/'s'/slug; out.mkdir(parents=True)
        (out/'index.html').write_text(tpl.replace('__SERIES_SLUG__',slug),encoding='utf-8')
        data_dir=DIST/'data'/slug; data_dir.mkdir(parents=True)
        published=json.loads(json.dumps(m))
        for episode in published.get('episodes',[]):
            publish_generated_audio(episode)
            for extra in episode.get('extras') or []:
                publish_generated_audio(extra)
        (data_dir/'series.json').write_text(json.dumps(published,ensure_ascii=False,indent=2),encoding='utf-8')
        assets=SERIES/slug/'assets'
        if assets.exists(): shutil.copytree(assets,data_dir/'assets',dirs_exist_ok=True)
        catalog.append({'slug':slug,'type':m['type'],'title':m['title'],'subtitle':m.get('subtitle',''),'episode_count':len(m['episodes'])})
    (DIST/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'status':'success-with-warnings' if WARN else 'success','series_count':len(manifests),'blocking':[],'warnings':WARN}
    (DIST/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Built {len(manifests)} series; warnings={len(WARN)}')
    return 0

if __name__=='__main__': raise SystemExit(main())
