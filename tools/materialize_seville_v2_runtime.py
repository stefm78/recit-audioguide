#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'seville-discovery-v2'
V2 = ROOT / 'series' / SLUG
V1 = ROOT / 'series' / 'seville-discovery'
PROGRAMS = [
    V2 / 'scenes' / 'FRIDAY_MORNING_SCENE_PROGRAM.json',
    V2 / 'scenes' / 'SATURDAY_SCENE_PROGRAM.json',
    V2 / 'scenes' / 'SUNDAY_SCENE_PROGRAM.json',
]
QUALIFICATIONS = [
    V2 / 'qualification' / 'J4_FRIDAY_MORNING_AUDIO_QUALIFICATION.json',
    V2 / 'qualification' / 'J4_SATURDAY_AUDIO_QUALIFICATION.json',
    V2 / 'qualification' / 'J4_SUNDAY_AUDIO_QUALIFICATION.json',
]
AUDIO_ROOT = V2 / 'assets' / 'audio'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def by_id(items):
    return {item['id']: item for item in items}


def route_url_map(v1):
    v1e = by_id(v1['episodes'])
    return {
        **{f'SEV2-FRI-AM-{i:02d}': v1e['seville-discovery-ep06']['maps_url'] for i in range(1, 7)},
        **{f'SEV2-FRI-AM-{i:02d}': v1e['seville-discovery-ep07']['maps_url'] for i in range(7, 9)},
        'SEV2-SAT-01': v1e['seville-discovery-ep00']['maps_url'],
        'SEV2-SAT-02': v1e['seville-discovery-ep00']['maps_url'],
        'SEV2-SAT-03': v1e['seville-discovery-ep05']['maps_url'],
        'SEV2-SAT-04': v1e['seville-discovery-ep05']['maps_url'],
        'SEV2-SAT-05': v1e['seville-discovery-ep01']['maps_url'],
        'SEV2-SAT-06': v1e['seville-discovery-ep01']['maps_url'],
        'SEV2-SAT-07': v1e['seville-discovery-ep03']['maps_url'],
        'SEV2-SAT-08': v1e['seville-discovery-ep03']['maps_url'],
        'SEV2-SUN-01': v1e['seville-discovery-g02']['maps_url'],
        'SEV2-SUN-02': v1e['seville-discovery-g02']['maps_url'],
        'SEV2-SUN-03': v1e['seville-discovery-g02']['maps_url'],
        'SEV2-SUN-04': 'https://www.google.com/maps/dir/?api=1&origin=Plaza%20de%20Toros%20de%20la%20Real%20Maestranza%20de%20Caballer%C3%ADa%20de%20Sevilla&destination=C.%20Agua%2C%205%2C%2041004%20Sevilla&waypoints=Pje.%20de%20Vila%2C%2011%2C%20Sevilla&travelmode=walking',
        'SEV2-SUN-05': v1e['seville-discovery-g13']['maps_url'],
        'SEV2-SUN-06': v1e['seville-discovery-g13']['maps_url'],
        'SEV2-SUN-07': v1e['seville-discovery-g13']['maps_url'],
        'SEV2-SUN-08': v1e['seville-discovery-g13']['maps_url'],
        'SEV2-SUN-09': 'https://www.google.com/maps/dir/?api=1&origin=Museo%20de%20Bellas%20Artes%20de%20Sevilla&destination=C.%20Agua%2C%205%2C%2041004%20Sevilla&travelmode=walking',
    }


def qualification_index():
    out = {}
    batches = []
    for path in QUALIFICATIONS:
        q = load(path)
        if q.get('status') != 'PASS':
            raise SystemExit(f'J4 qualification not PASS: {path}')
        run = q.get('qualification_run') or {}
        batches.append({
            'qualification_path': str(path.relative_to(ROOT)).replace('\\', '/'),
            'workflow_run_id': run.get('workflow_run_id'),
            'workflow_head_sha': run.get('workflow_head_sha'),
            'artifact_id': run.get('artifact_id'),
            'artifact_name': run.get('artifact_name'),
        })
        for entry in q['entries']:
            scene_id = entry['scene_id']
            if scene_id in out:
                raise SystemExit(f'duplicate J4 scene: {scene_id}')
            out[scene_id] = entry
    return out, batches


def all_scenes():
    rows = []
    scene_program_by_id = {}
    for path in PROGRAMS:
        p = load(path)
        for scene in p['scenes']:
            if scene['scene_id'] in scene_program_by_id:
                raise SystemExit(f'duplicate scene: {scene["scene_id"]}')
            scene_program_by_id[scene['scene_id']] = str(path.relative_to(ROOT)).replace('\\', '/')
            rows.append(scene)
    return rows, scene_program_by_id


def expected_scene_ids():
    return [*(f'SEV2-FRI-AM-{i:02d}' for i in range(1, 9)), *(f'SEV2-SAT-{i:02d}' for i in range(1, 9)), *(f'SEV2-SUN-{i:02d}' for i in range(1, 10))]


def materialize_descriptors():
    v1 = load(V1 / 'series.json')
    scenes, scene_program = all_scenes()
    expected = expected_scene_ids()
    ids = [scene['scene_id'] for scene in scenes]
    if ids != expected:
        raise SystemExit(f'primary scene order mismatch: {ids}')
    qindex, batches = qualification_index()
    if set(qindex) != set(expected):
        raise SystemExit('J4 qualified scene set != V2 primary scene set')
    routes = route_url_map(v1)
    episodes = []
    experience_episodes = {}
    manifest_entries = []
    for scene in scenes:
        sid = scene['scene_id']
        q = qindex[sid]
        base = AUDIO_ROOT / sid
        audio = base / 'audio.mp3'
        render_manifest = base / 'manifest.json'
        transcript = base / 'transcript.json'
        for required in (audio, render_manifest, transcript):
            if not required.is_file():
                raise SystemExit(f'missing qualified durable artifact: {required}')
        actual_audio = sha256(audio)
        if actual_audio != q['audio_sha256']:
            raise SystemExit(f'qualified MP3 hash mismatch for {sid}: {actual_audio} != {q["audio_sha256"]}')
        prefix = f'../../data/{SLUG}/assets/audio/{sid}'
        episodes.append({
            'id': sid,
            'day': 'day1' if sid.startswith('SEV2-FRI') else ('day2' if sid.startswith('SEV2-SAT') else 'day3'),
            'title': scene['short_label'],
            'stop': scene['route_section'],
            'location': scene['short_label'],
            'launch': scene['trigger_or_launch_condition'],
            'look': scene['observable_cue'],
            'summary': scene['primary_cue'],
            'maps_url': routes[sid],
            'audio_policy': 'packaged_sha256',
            'audio_sha256': q['audio_sha256'],
            'audio_url': f'{prefix}/audio.mp3',
            'transcript_url': f'{prefix}/transcript.json',
            'audio_manifest_url': f'{prefix}/manifest.json',
            'source_scene_program': scene_program[sid],
        })
        cues = [{'type': 'LOOK', 'text': scene['primary_cue']}]
        silence = scene.get('silence') or {}
        if silence.get('mode') == 'USER_PAUSE' and silence.get('prompt'):
            cues.append({'type': 'USER_PAUSE', 'text': silence['prompt']})
        experience_episodes[sid] = {
            'why': scene['short_label'],
            'look_first': scene['primary_cue'],
            'cues': cues,
            'cannot_find': (scene.get('fallback_behavior') or {}).get('cannot_find', ''),
            'source_refs': scene.get('source_refs') or [],
            'optional_depth_links': scene.get('optional_depth_links') or [],
        }
        manifest_entries.append({
            'scene_id': sid,
            'source_scene_program': scene_program[sid],
            'audio_path': str(audio.relative_to(ROOT)).replace('\\', '/'),
            'audio_sha256_expected_j4': q['audio_sha256'],
            'audio_sha256_published_source': actual_audio,
            'audio_sha256_match': True,
            'renderer_manifest_sha256': sha256(render_manifest),
            'transcript_sha256': sha256(transcript),
        })
    series = {
        'schema_version': 1,
        'slug': SLUG,
        'type': 'visit',
        'title': 'Séville V2 — guide de terrain audio-first',
        'subtitle': '25 scènes de terrain qualifiées, audio-first, avec version classique V1 disponible en repli immédiat.',
        'note': 'Runtime V2 matérialisé à partir des scènes J2 acceptées et des bytes MP3 J4 qualifiés; aucun nouveau rendu TTS.',
        'visit': {
            'start': v1['visit'].get('start'),
            'start_label': '3 jours · 25 scènes primaires · Google Maps reste l’autorité de navigation réelle',
            'navigation': 'geographic',
            'routing_provider': 'external_google_maps_with_accepted_v1_authority',
            'classic_fallback_url': '../seville-discovery/',
            'sunday_policy': {
                'primary_sequence': ['MAESTRANZA', 'CHECKOUT_LOCKERS_SILENCE', 'BELLAS_ARTES', 'PROTECTED_AIRPORT_DEPARTURE'],
                'casa_de_pilatos': 'FALLBACK_ONLY',
            },
        },
        'episodes': episodes,
    }
    experience = {
        'schema': 'recit.visit-experience.v2',
        'status': 'CANDIDATE',
        'series': SLUG,
        'principle': 'voir → écouter → comprendre → silence/mouvement → reprendre',
        'navigation_authority': 'external_real_conditions',
        'capabilities': {
            'audio_first_field_ui': {
                'enabled': True,
                'version': 2,
                'classic_fallback_url': '../seville-discovery/',
            }
        },
        'runtime_materialization': {
            'primary_scene_count': 25,
            'qualified_primary_audio_count': 25,
            'optional_depth_declared': 12,
            'optional_depth_audio_produced': 0,
            'optional_depth_disposition': 'DEFERRED',
            'sunday_primary_sequence': ['MAESTRANZA', 'CHECKOUT_LOCKERS_SILENCE', 'BELLAS_ARTES', 'PROTECTED_AIRPORT_DEPARTURE'],
            'casa_de_pilatos': 'FALLBACK_ONLY',
        },
        'episodes': experience_episodes,
    }
    runtime_manifest = {
        'schema': 'recit.seville-v2.runtime-audio-manifest.v1',
        'status': 'QUALIFIED_BYTES_PROMOTED',
        'policy': 'J4 artifact bytes are authoritative; no Edge TTS rerender is accepted as bit-for-bit equivalent.',
        'scene_count': 25,
        'hash_match_count': sum(1 for e in manifest_entries if e['audio_sha256_match']),
        'optional_depth_audio_count': 0,
        'j4_batches': batches,
        'entries': manifest_entries,
    }
    dump(V2 / 'series.json', series)
    dump(V2 / 'assets' / 'visit-experience.json', experience)
    dump(V2 / 'runtime-audio-manifest.json', runtime_manifest)


def patch_builder():
    path = ROOT / 'site' / 'build.py'
    text = path.read_text(encoding='utf-8')
    if 'def publish_packaged_audio(' in text:
        return
    text = text.replace('import json, os, shutil, sys\n', 'import hashlib, json, os, shutil, sys\n', 1)
    anchor = '\ndef publish_generated_audio(item, failed_ids):\n'
    if anchor not in text:
        raise SystemExit('site/build.py publish_generated_audio anchor not found')
    helper = r'''
def publish_packaged_audio(item, slug):
    if item.get('audio_policy') != 'packaged_sha256':
        return False
    item_id = item.get('id')
    expected = item.get('audio_sha256')
    if not item_id or not expected:
        raise RuntimeError(f'{slug}/{item_id}: packaged_sha256 requires id and audio_sha256')
    source = SERIES / slug / 'assets' / 'audio' / item_id
    audio = source / 'audio.mp3'
    if not audio.is_file():
        raise RuntimeError(f'{slug}/{item_id}: packaged audio missing: {audio}')
    actual = hashlib.sha256(audio.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError(f'{slug}/{item_id}: packaged audio sha256 mismatch: {actual} != {expected}')
    item['audio_url'] = f'../../data/{slug}/assets/audio/{item_id}/audio.mp3'
    transcript = source / 'transcript.json'
    if transcript.is_file():
        item['transcript_url'] = f'../../data/{slug}/assets/audio/{item_id}/transcript.json'
    manifest = source / 'manifest.json'
    if manifest.is_file():
        item['audio_manifest_url'] = f'../../data/{slug}/assets/audio/{item_id}/manifest.json'
    return True

'''
    text = text.replace(anchor, '\n' + helper + 'def publish_generated_audio(item, failed_ids):\n', 1)
    old = """    render_failed=episode_id in failed_ids
    generated=publish_generated_audio(episode, failed_ids)
"""
    new = """    render_failed=episode_id in failed_ids
    packaged=publish_packaged_audio(episode, slug)
    generated=False if packaged else publish_generated_audio(episode, failed_ids)
"""
    if old not in text:
        raise SystemExit('site/build.py classify anchor not found')
    text = text.replace(old, new, 1)
    old2 = """    episode['audio_source']='generated' if generated else ('fallback' if episode.get('audio_url') else 'none')
"""
    new2 = """    episode['audio_source']='packaged' if packaged else ('generated' if generated else ('fallback' if episode.get('audio_url') else 'none'))
"""
    if old2 not in text:
        raise SystemExit('site/build.py audio_source anchor not found')
    text = text.replace(old2, new2, 1)
    path.write_text(text, encoding='utf-8')


def main():
    materialize_descriptors()
    patch_builder()
    print('J6 runtime materialization descriptors and packaged-audio builder policy ready')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
