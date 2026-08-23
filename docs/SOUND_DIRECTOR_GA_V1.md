# Sound Director v1 — General Availability

Sound Director v1 est la couche éditoriale commune de `recit-audioguide` pour tous les usages audio. Elle est **disponible pour toute série et tout programme**, mais elle reste optionnelle épisode par épisode.

## Position dans la pile

```text
récit / visite / route / audiobook / learning
                ↓
        Sound Director v1
                ↓
      programme audio-engine v6
                ↓
           audio-engine
```

Le Sound Director décide de l’attention et de la dramaturgie. `audio-engine` exécute le mix. Aucun choix artistique n’est déplacé dans le moteur.

## Disponibilité

Les modes acceptés sont :

- `story` — récit, dialogue, action, fiction ou évocation historique ;
- `visit` — visite d’un lieu, priorité à l’espace réel et à l’intelligibilité ;
- `route` — écoute en mouvement/voiture, voix très prioritaire ;
- `audiobook` — continuité longue durée, habillage exceptionnel plutôt que permanent ;
- `learning` — l’habillage doit servir compréhension ou mémorisation.

Les trois premiers sont les usages actuels de Récit Audioguide. `audiobook` et `learning` rendent le contrat portable sans créer un nouveau moteur ; leur extraction vers un composant partagé n’est justifiée que lorsqu’un second produit les consommera réellement.

## Densité

Chaque sidecar choisit explicitement :

- `none` — aucune intervention sonore ajoutée ;
- `light` — quelques accents, silences, espaces ou transitions ;
- `scene-rich` — mise en scène plus construite lorsque le récit le justifie.

`none` est une sortie parfaitement valide. La couverture des sidecars peut augmenter progressivement et ne bloque jamais un programme qui n’a pas encore été dirigé.

## Artefacts

- Contrat : `docs/sound-direction.schema.json`
- Profils : `docs/sound-direction-profiles-v1.json`
- Principes éditoriaux : `docs/SOUND_DIRECTION_V1.md`
- Outil : `python tools/sound_direction.py`
- Référence artistique : `series/_showcase/direction/showcase-orleans-1710-gold.direction.json`

## Usage

Créer un sidecar vide :

```bash
python tools/sound_direction.py scaffold \
  series/<serie>/audio/<episode>.json \
  --mode story \
  --density light
```

Le sidecar doit ensuite être **dirigé** par un auteur ou une IA : beats, propriétaire de l’attention, raison de chaque couche, trajectoire de diction, silence et handoffs. Le scaffold ne remplace pas cette décision artistique.

Valider tous les sidecars présents :

```bash
python tools/sound_direction.py validate
```

Le validateur affiche aussi la couverture du catalogue. L’absence d’un sidecar est non bloquante ; un sidecar présent mais invalide est une erreur.

## Règle de promotion

Le Sound Director est GA dans `recit-audioguide`. Il ne devient un repo ou service autonome que lorsqu’au moins un second consommateur réel (par exemple Learn-it ou une chaîne audiobook) exige la même logique. Jusque-là, extraction interdite : pas de microservice, pas de nouveau repo, pas de dépendance supplémentaire.
