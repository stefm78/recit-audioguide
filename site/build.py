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
        for extra in e.get('extras') or []:
            extra_id=extra.get('id')
            if extra_id:
                if extra_id in ids: BLOCK.append(f'{path}: id audio dupliqué {extra_id}')
                ids.add(extra_id)
    return data


def load_render_failures():
    path=ROOT/'generated'/'audio'/'render-report.json'
    if not path.exists(): return set(), None
    try:
        report=json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        WARN.append(f'render-report.json illisible: {e}')
        return set(), None
    failed={item.get('id') for item in report.get('failures') or [] if item.get('id')}
    return failed, report


def generated_asset(directory: Path, *names):
    for name in names:
        if (directory/name).exists(): return name
    return None


def publish_generated_audio(item, failed_ids):
    item_id=item.get('id')
    if not item_id or item_id in failed_ids:
        return False
    generated=ROOT/'generated'/'audio'/item_id
    audio_name=generated_asset(generated,'audio.mp3','guide.mp3')
    if not audio_name:
        return False
    target=DIST/'audio'/item_id
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(generated,target,dirs_exist_ok=True)
    item['audio_url']=f"../../audio/{item_id}/{audio_name}"
    transcript_name=generated_asset(generated,'transcript.json','resolved-cast.json')
    if transcript_name:
        item['transcript_url']=f"../../audio/{item_id}/{transcript_name}"
    if (generated/'manifest.json').exists():
        item['audio_manifest_url']=f"../../audio/{item_id}/manifest.json"
    return True


def classify_episode(episode, series_type, slug, failed_ids):
    issues=[]
    episode_id=episode.get('id')
    render_failed=episode_id in failed_ids
    generated=publish_generated_audio(episode, failed_ids)

    if render_failed:
        if episode.get('audio_url'):
            issues.append('nouveau rendu audio échoué; repli existant conservé')
        else:
            issues.append('rendu audio échoué')
    if not episode.get('audio_url'):
        issues.append('audio absent')
    if not episode.get('summary'):
        issues.append('résumé absent')
    if series_type=='route' and not episode.get('launch'):
        issues.append('repère de lancement absent')

    for j,extra in enumerate(episode.get('extras') or [],1):
        extra_failed=extra.get('id') in failed_ids if extra.get('id') else False
        publish_generated_audio(extra, failed_ids)
        if extra_failed and extra.get('audio_url'):
            issues.append(f'bonus {j}: nouveau rendu échoué; repli existant conservé')
        elif not extra.get('audio_url'):
            issues.append(f'bonus {j}: audio absent')

    state='ready'
    if not episode.get('audio_url'):
        state='failed'
    elif issues:
        state='warning'
    episode['state']=state
    if issues:
        episode['issues']=issues
        WARN.extend(f'{slug}/{episode_id}: {issue}' for issue in issues)
    else:
        episode.pop('issues',None)
    episode['audio_source']='generated' if generated else ('fallback' if episode.get('audio_url') else 'none')
    return state


def series_state(episode_states):
    if not episode_states or all(state=='failed' for state in episode_states):
        return 'blocked'
    if any(state!='ready' for state in episode_states):
        return 'degraded'
    return 'ready'


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

    failed_ids, render_report=load_render_failures()
    if DIST.exists(): shutil.rmtree(DIST)
    (DIST/'assets').mkdir(parents=True)
    (DIST/'s').mkdir()
    (DIST/'data').mkdir()
    shutil.copy2(WEB/'index.html',DIST/'index.html')
    for name in ('styles.css','home.js','app.js'): shutil.copy2(WEB/name,DIST/'assets'/name)
    tpl=(WEB/'series.html').read_text(encoding='utf-8')
    catalog=[]
    series_reports=[]

    for m in manifests:
        slug=m['slug']
        out=DIST/'s'/slug; out.mkdir(parents=True)
        (out/'index.html').write_text(tpl.replace('__SERIES_SLUG__',slug),encoding='utf-8')
        data_dir=DIST/'data'/slug; data_dir.mkdir(parents=True)
        published=json.loads(json.dumps(m))
        states=[]
        for episode in published.get('episodes',[]):
            states.append(classify_episode(episode,published['type'],slug,failed_ids))
        published['state']=series_state(states)
        (data_dir/'series.json').write_text(json.dumps(published,ensure_ascii=False,indent=2),encoding='utf-8')
        assets=SERIES/slug/'assets'
        if assets.exists(): shutil.copytree(assets,data_dir/'assets',dirs_exist_ok=True)
        catalog.append({
            'slug':slug,
            'type':m['type'],
            'title':m['title'],
            'subtitle':m.get('subtitle',''),
            'episode_count':len(m['episodes']),
            'state':published['state'],
        })
        series_reports.append({
            'slug':slug,
            'state':published['state'],
            'episodes':[{'id':e.get('id'),'state':e.get('state')} for e in published.get('episodes',[])],
        })

    (DIST/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    overall='ready' if all(item['state']=='ready' for item in series_reports) and not WARN else 'degraded'
    report={
        'status':overall,
        'series_count':len(manifests),
        'blocking':[],
        'warnings':WARN,
        'production_status':render_report.get('status') if render_report else None,
        'series':series_reports,
    }
    (DIST/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Built {len(manifests)} series; state={overall}; warnings={len(WARN)}')
    return 0

if __name__=='__main__': raise SystemExit(main())
