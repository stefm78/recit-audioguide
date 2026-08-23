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
    return data


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
            generated=ROOT/'generated'/'audio'/episode['id']
            if (generated/'guide.mp3').exists():
                target=DIST/'audio'/episode['id']
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copytree(generated,target,dirs_exist_ok=True)
                episode['audio_url']=f"../../audio/{episode['id']}/guide.mp3"
                if (generated/'resolved-cast.json').exists():
                    episode['transcript_url']=f"../../audio/{episode['id']}/resolved-cast.json"
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
