#!/usr/bin/env python3
import json
from pathlib import Path

PATH = Path("series/nuit-apres-orleans/audio/nuit-apres-orleans-ep01.json")
data = json.loads(PATH.read_text(encoding="utf-8"))

if data.get("id") != "nuit-apres-orleans-ep01":
    raise SystemExit("Unexpected program id")
segments = data.get("segments") or []
if len(segments) != 150:
    raise SystemExit(f"Expected 150 segments, got {len(segments)}")

changes = {
    3: (
        "Personne ne lui a posé la question. Un choc sec claque quelque part dans la rue. Puis une cloche se met à sonner. Une autre lui répond, plus loin. Cette fois, des pas dévalent l'escalier.",
        "Personne ne lui a posé la question. Un choc sec claque quelque part dans la rue. Martin se fige. Puis, dehors, quelque chose change.",
    ),
    30: (
        "Vous allez tous les deux descendre jusqu'à Blois.",
        "Le paquet doit descendre jusqu'à Blois. Vous, vous l'emmenez d'abord jusqu'à notre halte avant Meung.",
    ),
    34: (
        "Vous suivez la rive, vous ne jouez pas aux soldats, vous ne débarquez pas si vous voyez des hommes armés, et si je dis que le fleuve est encore dangereux, tu ne réponds pas que tu le connais.",
        "Là, vous attendez Pierre et des nouvelles sûres. Vous n'essayez pas de passer Meung seuls, vous ne naviguez pas de nuit, vous ne débarquez pas si vous voyez des hommes armés, et si je dis que le fleuve est encore dangereux, tu ne réponds pas que tu le connais.",
    ),
    89: (
        "Derrière eux, les cloches sont plus petites. Une seule domine encore les autres. Puis elle aussi s'éloigne.",
        "Orléans ne remplit plus tout l'horizon. Les toits se tassent derrière eux, la fumée se mêle au soir. Agnès ne parle plus. Martin rame.",
    ),
    90: (
        "Quand elle disparaît enfin, Martin découvre quelque chose qu'il n'avait pas remarqué depuis des mois : le silence n'est pas silencieux. Il y a l'eau contre le bois. Le frottement d'une corde. Le souffle d'Agnès. Un oiseau quelque part sur la rive. Et le bruit régulier de l'aviron qui entre dans la Loire.",
        "Puis plus rien de la ville. Martin écoute. Ce qu'il prenait pour du silence est en réalité un autre monde, plus bas, plus proche.",
    ),
    150: (
        "Martin garde la main sur le sac. La Loire coule dans le noir. Devant eux, quelque part, il y a Blois. Et désormais, peut-être, des gens qui les attendent.",
        "Martin garde la main sur le sac. Devant eux, quelque part, il y a Blois. Et désormais, peut-être, des gens qui les attendent.",
    ),
}

for number, (old, new) in changes.items():
    segment = segments[number - 1]
    current = segment.get("text")
    if current == old:
        segment["text"] = new
    elif current != new:
        raise SystemExit(f"Segment {number} drifted; refusing blind rewrite: {current!r}")

segments[149]["pause_after_ms"] = 1500

note = data.get("historical_note", "")
addition = " Après la levée du siège, des positions anglaises subsistent sur la Loire, notamment à Meung-sur-Loire et Beaugency jusqu'à la campagne de juin ; la halte avant Meung et Pierre sont des éléments fictifs destinés à faire de cette contrainte militaire une cause dramatique explicite."
if addition.strip() not in note:
    data["historical_note"] = note.rstrip() + addition

source = "https://www.orleans-metropole.fr/sites/default/files/2020-05/fiche_pedagogique_jeanne_d_arc_2020.pdf"
sources = data.setdefault("sources", [])
if source not in sources:
    sources.append(source)

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Applied La nuit après Orléans prototype V2")
