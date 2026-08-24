#!/usr/bin/env python3
import json
import re
from pathlib import Path

PATH = Path("series/nuit-apres-orleans/audio/nuit-apres-orleans-ep01.json")
data = json.loads(PATH.read_text(encoding="utf-8"))
if data.get("id") != "nuit-apres-orleans-ep01":
    raise SystemExit("Unexpected program id")
segments = data.get("segments") or []
if len(segments) != 150:
    raise SystemExit(f"Expected 150 segments, got {len(segments)}")

data["production_version"] = 4

edits = {
    1: "Au début, Martin ne voit rien. Il est couché sur le ventre sous une table, une joue contre des dalles froides. Au-dessus de lui, quelque chose tremble dans un gobelet. Dehors, un grondement roule, s'arrête, puis revient. Il retient son souffle et écoute. Le gobelet recommence à trembler.",
    2: "Ça venait du pont ?",
    3: "Personne ne lui répond. Un choc sec claque quelque part dans la rue. Martin se fige. Puis, dehors, quelque chose change.",
    53: "Martin retourne le paquet entre ses doigts. Le sceau lui paraît presque décevant : un peu de cire marquée d'une empreinte. Pourtant, ce petit morceau de cire n'est pas un décor. Il dit qu'un acte a été reconnu et validé par celui qui l'a scellé. Martin sait peu lire. Mais il comprend très bien une chose : s'il brise cette cire, il ne pourra pas la remettre comme avant.",
    74: "Tu l'as vraiment vue, Jeanne ?",
    77: "Je l'ai vue passer, oui.",
    78: "De près, cette fois ?",
    79: "Pas vraiment près.",
    80: "Et elle t'a regardé ?",
    83: "Ton père... tu l'as vraiment vu travailler pour eux ?",
    85: "D'accord...",
    87: "Et toi, tu le crois ?",
    106: "Là, regarde.",
    110: "Pas que je voie.",
    143: "Il me regardait comme si",
}
for number, text in edits.items():
    segments[number - 1]["text"] = text

# French-language integrity: this prototype uses only monolingual fr-FR provider voices.
for segment in segments:
    cid = segment.get("character_id")
    if cid == "narrateur":
        segment.pop("preset", None)
        segment["voice"] = "fr-FR-DeniseNeural"
        segment["rate"] = "-5%"
        segment["pitch"] = "-8Hz"
        segment["volume"] = "+1%"
    elif cid == "martin":
        segment.pop("preset", None)
        old_voice = segment.get("voice", "")
        old_pitch = segment.get("pitch", "+20Hz")
        match = re.fullmatch(r"([+-]?\d+)Hz", old_pitch)
        pitch = int(match.group(1)) if match else 20
        if "Multilingual" in old_voice:
            pitch = max(14, min(22, pitch - 5))
        segment["voice"] = "fr-FR-HenriNeural"
        segment["pitch"] = f"{pitch:+d}Hz"
        segment["volume"] = "+2%"
    elif cid == "agnes":
        segment.pop("preset", None)
        old_voice = segment.get("voice", "")
        old_pitch = segment.get("pitch", "+7Hz")
        match = re.fullmatch(r"([+-]?\d+)Hz", old_pitch)
        pitch = int(match.group(1)) if match else 7
        if old_voice == "fr-FR-EloiseNeural":
            pitch = max(5, min(10, pitch + 11))
        segment["voice"] = "fr-FR-DeniseNeural"
        segment["pitch"] = f"{pitch:+d}Hz"
        segment["volume"] = "+1%"

pause_values = [
220,120,100,100,110,80,250,300,380,110,180,250,90,70,80,70,110,300,300,240,
90,70,60,70,260,220,260,90,150,220,90,160,220,180,80,260,220,90,120,80,
120,90,150,100,210,280,240,360,130,170,110,220,260,90,60,110,80,60,230,140,
480,180,70,70,330,220,90,50,70,50,160,250,220,110,60,90,110,70,90,110,
320,160,190,300,170,300,100,320,250,220,220,260,420,220,60,50,80,160,220,70,
110,150,100,180,220,90,220,140,60,60,180,170,90,50,90,100,90,60,90,150,
100,55,60,90,90,60,90,130,55,55,90,130,330,140,100,60,120,130,150,70,
80,60,20,170,180,220,90,70,300,1500]
if len(pause_values) != 150:
    raise SystemExit("Pause map must contain 150 values")
for segment, pause in zip(segments, pause_values):
    segment["pause_after_ms"] = pause

soundscape = data.setdefault("soundscape", {})
events = soundscape.setdefault("events", [])

def ensure_event(event):
    key = (event.get("sound"), event.get("role"), event.get("after_segment"))
    if not any((e.get("sound"), e.get("role"), e.get("after_segment")) == key for e in events):
        events.append(event)

ensure_event({
    "sound": "historic-horse-hooves", "role": "scene", "after_segment": 11,
    "space_ms": 1500, "gain_db": -26, "placement": "left",
    "fade_in_ms": 120, "fade_out_ms": 650
})
ensure_event({
    "sound": "historic-horse-hooves", "role": "bridge", "after_segment": 65,
    "foreground_ms": 900, "carry_through_segments": 1, "tail_ms": 0,
    "gain_db": -31, "placement": "right", "fade_in_ms": 180, "fade_out_ms": 650
})
events.sort(key=lambda e: (e.get("after_segment", 10**9), e.get("sound", "")))
soundscape["ducking"] = "speech"

for number, segment in enumerate(segments, 1):
    voice = segment.get("voice", "")
    if "Multilingual" in voice:
        raise SystemExit(f"Segment {number} still uses multilingual voice {voice}")

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Applied La nuit après Orléans V3: monolingual casting, semantic cadence, stronger sound world")
