#!/usr/bin/env python3
import argparse, json, shutil
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--p4-dir", required=True)
    ap.add_argument("--p6-dir", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    p4=Path(args.p4_dir); p6=Path(args.p6_dir); out=Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    p4_manifest=load(p4/"manifest.json")
    p6_manifest=load(p6/"manifest.json")
    if p4_manifest.get("status")!="MACHINE_PASS":
        raise SystemExit("P4_NOT_MACHINE_PASS")
    if p6_manifest.get("status")!="MACHINE_PASS":
        raise SystemExit("P6_NOT_MACHINE_PASS")
    if p4_manifest.get("cloud_tts") is not False or p6_manifest.get("cloud_tts") is not False:
        raise SystemExit("CLOUD_POLICY_REJECT")

    shutil.copy2(p4/"p4-voxcpm2-a.mp3", out/"p4.mp3")
    shutil.copy2(p6/"p6-qwen3-hybrid.mp3", out/"p6.mp3")
    shutil.copy2(p4/"manifest.json", out/"p4-manifest.json")
    shutil.copy2(p6/"manifest.json", out/"p6-manifest.json")

    meta={
      "schema":"odyssee-stream2-batched-review-v1",
      "p4_candidate_sha256":p4_manifest["results"][0]["candidate_sha256"],
      "p6_candidate_sha256":p6_manifest["candidate_sha256"],
      "cloud_tts_forbidden":True,
      "human_gate":"PENDING",
    }
    (out/"review-manifest.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    impact="".join(f"<label><input type=radio name=p6_impact value={n}> {n}/5</label>" for n in range(1,6))
    html=f"""<!doctype html><html lang='fr'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Odyssée — Stream 2 review</title>
<style>body{{font-family:system-ui,sans-serif;max-width:920px;margin:2rem auto;padding:0 1rem;line-height:1.45}}.card{{border:1px solid #999;border-radius:14px;padding:1rem;margin:1.25rem 0}}audio{{width:100%}}label{{display:block;margin:.45rem 0}}fieldset{{margin:1rem 0}}button{{padding:.7rem 1rem}}textarea{{width:100%;min-height:18rem}}</style>
<h1>Odyssée — P4 + P6</h1>
<p>Une seule écoute humaine. Les deux candidats sont déjà machine PASS et sans cloud TTS.</p>
<section class='card'><h2>P4 — Sirènes</h2><audio controls preload='metadata' src='p4.mp3'></audio>
<fieldset><legend>Attraction</legend><label><input type=radio name=p4_attraction value=PASS> PASS — envie qu’Ulysse continue d’écouter</label><label><input type=radio name=p4_attraction value=BORDERLINE> BORDERLINE</label><label><input type=radio name=p4_attraction value=FAIL> FAIL</label></fieldset>
<fieldset><legend>Français</legend><label><input type=radio name=p4_french value=PASS> PASS</label><label><input type=radio name=p4_french value=FAIL> FAIL</label></fieldset>
<fieldset><legend>Polyphonie</legend><label><input type=radio name=p4_polyphony value=PASS> utile PASS</label><label><input type=radio name=p4_polyphony value=FAIL> FAIL</label></fieldset>
<fieldset><legend>Cliché</legend><label><input type=radio name=p4_cliche value=NONE> AUCUN</label><label><input type=radio name=p4_cliche value=LIGHT> LÉGER</label><label><input type=radio name=p4_cliche value=HEAVY> FORT</label></fieldset>
<fieldset><legend>Adresse à Ulysse</legend><label><input type=radio name=p4_addressed value=PASS> PASS</label><label><input type=radio name=p4_addressed value=FAIL> FAIL</label></fieldset></section>
<section class='card'><h2>P6 — Ulysse émotionnel</h2><audio controls preload='metadata' src='p6.mp3'></audio>
<fieldset><legend>Impact émotionnel</legend>{impact}</fieldset>
<fieldset><legend>Réaction d’Ulysse</legend><label><input type=radio name=p6_reaction value=PASS> PASS</label><label><input type=radio name=p6_reaction value=FAIL> FAIL</label></fieldset>
<fieldset><legend>Identité Ulysse</legend><label><input type=radio name=p6_identity value=PASS> même personnage PASS</label><label><input type=radio name=p6_identity value=FAIL> FAIL</label></fieldset>
<fieldset><legend>Français</legend><label><input type=radio name=p6_french value=PASS> PASS</label><label><input type=radio name=p6_french value=FAIL> FAIL</label></fieldset>
<fieldset><legend>Mélodrame</legend><label><input type=radio name=p6_melodrama value=NONE> aucun</label><label><input type=radio name=p6_melodrama value=PRESENT> présent</label></fieldset>
<fieldset><legend>Pénélope / mise en scène H1b-B</legend><label><input type=radio name=p6_staging value=PASS> non régressée PASS</label><label><input type=radio name=p6_staging value=FAIL> régression</label></fieldset></section>
<button id=export>Produire le verdict JSON</button><textarea id=out></textarea>
<script>
const v=n=>document.querySelector('input[name="'+n+'"]:checked')?.value||null;
document.getElementById('export').onclick=()=>{{const r={{schema:'odyssee-stream2-human-review-v1',p4:{{attraction:v('p4_attraction'),french:v('p4_french'),polyphony:v('p4_polyphony'),cliche:v('p4_cliche'),addressed:v('p4_addressed')}},p6:{{impact:Number(v('p6_impact'))||null,reaction:v('p6_reaction'),identity:v('p6_identity'),french:v('p6_french'),melodrama:v('p6_melodrama'),staging:v('p6_staging')}}}};const t=JSON.stringify(r,null,2);document.getElementById('out').value=t;navigator.clipboard?.writeText(t);}};
</script></html>"""
    (out/"index.html").write_text(html,encoding="utf-8")

if __name__=="__main__":
    main()
