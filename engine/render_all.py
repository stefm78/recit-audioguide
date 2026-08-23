#!/usr/bin/env python3
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; GENERATED=ROOT/'generated'; AUDIO=GENERATED/'audio'; PALETTE=ROOT/'engine'/'voice-palette.json'; RENDERER=ROOT/'engine'/'render_audioguide_fr.py'

def digest(*paths):
    h=hashlib.sha256()
    for p in paths: h.update(Path(p).read_bytes())
    return h.hexdigest()

def main():
    warnings=[]; rendered=0; cached=0
    for manifest_path in sorted((ROOT/'series').glob('*/series.json')):
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for e in manifest.get('episodes',[]):
            src=e.get('source_file')
            if not src: continue
            src_path=manifest_path.parent/src
            if not src_path.exists(): warnings.append(f"{e.get('id')}: source_file absent: {src}"); continue
            out=AUDIO/e['id']; marker=out/'render.sha'; expected=digest(src_path,PALETTE,ROOT/'engine'/'render_audioguide.py',RENDERER)
            if (out/'guide.mp3').exists() and marker.exists() and marker.read_text().strip()==expected: cached+=1; continue
            try:
                subprocess.run([sys.executable,str(RENDERER),str(src_path),'--palette',str(PALETTE),'--output-root',str(AUDIO)],check=True,timeout=900)
                marker.write_text(expected+'\n'); rendered+=1
            except Exception as exc:
                warnings.append(f"{e.get('id')}: rendu audio échoué ({exc})")
    GENERATED.mkdir(exist_ok=True)
    (GENERATED/'render-report.json').write_text(json.dumps({'rendered':rendered,'cached':cached,'warnings':warnings},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'audio rendered={rendered} cached={cached} warnings={len(warnings)}')
    for w in warnings: print('WARN:',w,file=sys.stderr)
    return 0
if __name__=='__main__': raise SystemExit(main())
