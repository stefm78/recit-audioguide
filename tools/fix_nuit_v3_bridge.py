#!/usr/bin/env python3
import json
from pathlib import Path
p=Path('series/nuit-apres-orleans/audio/nuit-apres-orleans-ep01.json')
d=json.loads(p.read_text(encoding='utf-8'))
found=False
for e in d.get('soundscape',{}).get('events',[]):
    if e.get('sound')=='historic-horse-hooves' and e.get('role')=='bridge' and e.get('after_segment')==65:
        e['foreground_ms']=1000
        found=True
if not found:
    raise SystemExit('Target horse bridge not found')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
