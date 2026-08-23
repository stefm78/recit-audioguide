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

Chaque décision choisit explicitement :

- `none` — aucune intervention sonore ajoutée ;
- `light` — quelques accents, silences, espaces ou transitions ;
- `scene-rich` — mise en scène plus construite lorsque le récit le justifie.

`none` est une sortie parfaitement valide. La densité est un plafond artistique, jamais un quota d’effets.

## Deux niveaux, pas 73 dossiers artificiels

Le rollout complet utilise deux niveaux complémentaires :

1. `series/sound-direction-review-v1.json` contient **une décision pour chaque programme réel** : `keep`, `direct` ou `enhance`, avec la densité retenue. Cette revue doit couvrir 100 % du catalogue réel.
2. `series/<serie>/direction/*.direction.json` n’existe que lorsqu’une direction scène par scène apporte quelque chose. Un programme marqué `enhance` doit obligatoirement disposer de ce sidecar détaillé.

Cette séparation évite de créer des dizaines de sidecars vides simplement pour afficher 100 % de couverture. `keep` signifie que le Sound Director a réellement revu l’épisode et arbitré en faveur de la sobriété ; ce n’est pas un épisode oublié.

## Artefacts

- Contrat : `docs/sound-direction.schema.json`
- Profils : `docs/sound-direction-profiles-v1.json`
- Politique par série : `series/sound-direction-catalog.json`
- Revue complète : `series/sound-direction-review-v1.json`
- Principes éditoriaux : `docs/SOUND_DIRECTION_V1.md`
- Outil : `python tools/sound_direction.py`
- Référence artistique : `series/_showcase/direction/showcase-orleans-1710-gold.direction.json`

## Usage

Créer un sidecar détaillé :

```bash
python tools/sound_direction.py scaffold \
  series/<serie>/audio/<episode>.json \
  --mode story \
  --density light
```

Le sidecar doit ensuite être **dirigé** par un auteur ou une IA : beats, propriétaire de l’attention, raison de chaque couche, trajectoire de diction, silence et handoffs. Le scaffold ne remplace pas cette décision artistique.

Valider catalogue, revue complète et sidecars détaillés :

```bash
python tools/sound_direction.py validate
```

Le validateur exige : les 8 séries réelles calibrées, une décision de revue pour chaque programme réel, aucun doublon/oubli, cohérence de densité, et un sidecar détaillé pour chaque décision `enhance`.

## Règle de promotion

Le Sound Director est GA dans `recit-audioguide`. Il ne devient un repo ou service autonome que lorsqu’au moins un second consommateur réel (par exemple Learn-it ou une chaîne audiobook) exige la même logique. Jusque-là, extraction interdite : pas de microservice, pas de nouveau repo, pas de dépendance supplémentaire.
