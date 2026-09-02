# P6 — Ulysse — protocole de performance humaine source V1

## Statut actuel

Le casting P6 est fermé :

`ULYSSES_EMOTIONAL_HUMAN_PASS`

La capability acceptée est :

`performance humaine française -> BeltOut -> identité Henri/Ulysse`

Il ne reste plus de recherche de casting. Le travail humain restant est exclusivement une **capture Production propre des 12 segments Ulysse gelés de S15**.

État attendu avant réception :

`P6_S15_PRODUCTION_HUMAN_CAPTURE_PENDING`

Autorités :

- `series/odyssee/production/P6_FROZEN_S15_BINDING_V1.json`
- `series/odyssee/production/P6_STREAM3_READINESS_V1.json`
- `series/odyssee/production/provider-packages/P6_ULYSSES_HUMAN_BELTOUT_PRODUCTION_V1.json`
- `series/odyssee/production/P6_S15_PRODUCTION_CAPTURE_V1.json`

## Principe

La performance humaine fournit uniquement :

- rythme ;
- respiration ;
- intention ;
- retenue ;
- émotion ;
- naturel du français.

BeltOut fournit le timbre cible Henri/Ulysse.

Le comédien source n’a pas besoin de ressembler à Henri. La prise source doit surtout être naturelle, propre et proche de la direction acceptée.

## Direction commune acceptée

Ulysse n’est pas en représentation. Il est chez lui, très près de Pénélope, après vingt ans.

Jouer :

- proche et intime ;
- français quotidien ;
- aucune projection héroïque ;
- émotion réelle mais non fabriquée ;
- pas de cri ;
- pas de chuchotement systématique ;
- pas de sanglot forcé ;
- pas de voix de bande-annonce.

La qualification humaine a observé une coloration mélodramatique `PRESENT`, puis l’a jugée artistiquement appropriée. En Production, cette coloration peut donc exister **si elle naît naturellement** ; elle ne doit jamais être recherchée comme effet.

## Production S15 — 12 segments exacts

Une seule prise gelée par segment est remise au pipeline.

| Segment | Texte exact | Groupe / intention |
|---:|---|---|
| 112 | `Quoi ?` | bed-shock — choc personnel immédiat, bas, sans cri |
| 114 | `On ne peut pas.` | bed-shock — certitude intime, pas de démonstration |
| 116 | `Tu le sais.` | bed-shock — tension personnelle, proximité |
| 118 | `On ne peut pas déplacer ce lit.` | bed-shock — certitude plus forte que colère |
| 120 | `Non.` | bed-shock — refus réflexe, contenu |
| 133 | `Et si l’arbre a été coupé—` | tree-wound — blessure contenue ; la voix peut accrocher |
| 135 | `Alors tu aurais dû le savoir.` | tree-wound — douleur intime, sans surjeu |
| 140 | `Quoi ?` | test-reveal — choc qui devient compréhension |
| 142 | `Alors pourquoi—` | test-reveal — question interrompue par la reconnaissance |
| 151 | `L’olivier.` | test-reveal — compréhension simple, moins de projection |
| 153 | `Tu savais.` | test-reveal — reconnaissance bouleversée mais contenue |
| 158 | `Pénélope.` | test-reveal — nom intime, sans déclaration |

Aucun autre segment Ulysse n’est recasté par P6.

## Surface Web Production

Utiliser :

`web/reviews/odyssee-p6-human-performance.html`

La surface :

- affiche les 12 textes exacts gelés ;
- affiche le contexte S15 exact avant/après chaque ligne ;
- propose une écoute dramaturgique H1b-B ;
- permet plusieurs prises par segment ;
- conserve les prises uniquement dans IndexedDB local ;
- permet l’écoute locale de chaque prise ;
- impose une sélection explicite d’une seule prise par segment ;
- impose une confirmation explicite de propreté de la prise ;
- bloque l’export tant que les 12 segments ne sont pas complets ;
- exporte uniquement les 12 prises retenues + `recording-manifest.json` + `SHA256SUMS.txt` + `README.txt` ;
- n’effectue aucun upload automatique.

La base IndexedDB Production est distincte de l’ancien studio de probe afin qu’aucune prise historique ne puisse être sélectionnée par accident.

## Référence dramaturgique et probe historique

L’audio H1b-B peut être écouté pour comprendre :

- la proximité ;
- Pénélope ;
- les pauses ;
- la trajectoire de la scène.

Il n’est **jamais** une source Production.

Le probe humain bruité/clické qui a servi à qualifier la capability P6 ne doit pas être réutilisé, copié, converti ou injecté dans S15.

## Capture

Avant gel, sont autorisés :

- répétition ;
- retakes ;
- écoute de ses propres prises ;
- comparaison humaine locale ;
- choix d’une prise propre.

Qualité recherchée :

- pièce calme ;
- bouche environ 15–30 cm du micro ;
- micro/téléphone immobile ;
- aucun clic de manipulation ;
- aucun toucher du téléphone ou clavier pendant la phrase ;
- aucun clipping ;
- 200–500 ms environ de room tone propre avant/après si possible ;
- pas de musique ;
- pas de réverbération ajoutée ;
- pas de réduction de bruit agressive ;
- pas d’auto-level ou compression audible.

WAV mono 44.1/48 kHz est préférable. WebM/M4A/MP3 propre reste acceptable : le pipeline peut effectuer une normalisation déterministe de conteneur/codec.

## Gel avant conversion

Le gel intervient **avant toute conversion BeltOut**.

Conditions :

- 12/12 segments ;
- exactement une prise retenue par segment ;
- chaque prise écoutée et confirmée propre ;
- SHA-256 calculé dans le navigateur ;
- manifeste exporté avec les 12 hashes.

Après le gel :

- aucune substitution de prise après écoute d’une sortie BeltOut ;
- aucun best-of-N ;
- aucun second pass BeltOut ;
- aucune correction émotionnelle DSP ;
- aucun time-stretch ;
- aucun pitch-shift.

## Après réception du ZIP

Stream 3 doit :

1. vérifier le ZIP et les SHA-256 ;
2. vérifier l’exactitude segment/texte 12/12 ;
3. vérifier que chaque fichier est fini, non silencieux et non saturé ;
4. geler les 12 prises ;
5. appliquer exactement **une conversion BeltOut par prise sélectionnée** ;
6. utiliser le seed déterministe `202609060000 + segment S15` ;
7. appliquer uniquement un alignement de niveau constant, dans la limite déclarée par le package ;
8. préserver la durée et les pauses de scène ;
9. composer avec Pénélope déjà matérialisée ;
10. exécuter l’automatic QA S15 puis la qualification Block D.

Une normalisation de codec/conteneur est permise si techniquement nécessaire. Aucune correction artistique n’est permise après gel.

## Confidentialité

La voix humaine brute :

- reste locale jusqu’à l’export volontaire du ZIP ;
- ne doit jamais être commitée dans le repository public ;
- ne doit jamais être publiée dans une GitHub Release publique.

Seuls les outputs Production autorisés après conversion peuvent entrer dans le pipeline de publication.

## Historique — probe capability 5 lignes

Les anciennes cinq lignes (`Non.`, `Ce lit ne sort pas de cette chambre.`, `Tu le savais.`, `Pénélope…`, `Notre lit.`) sont des artefacts de **qualification de capability** uniquement.

Elles ne constituent pas le mapping Production S15 et ne doivent pas être utilisées comme substitutions des 12 segments gelés.

## Intake Stream 3 — hors repository public

Après export du ZIP, l'intake est effectué avec :

```bash
python tools/p6_s15_pipeline.py intake <ZIP> --private-out <DOSSIER_PRIVE_HORS_REPO>
```

Le dossier `--private-out` **doit être situé hors du checkout Git public**. L'outil refuse explicitement une destination sous le repository.

Le gate vérifie avant toute conversion :

- manifeste de capture Production attendu ;
- exactement les 12 segments S15 gelés ;
- texte exact de chaque segment ;
- une seule prise sélectionnée par segment ;
- confirmation de propreté 12/12 ;
- SHA-256 de chaque audio ;
- cohérence avec `SHA256SUMS.txt` ;
- aucun fichier audio supplémentaire ou membre ZIP inattendu ;
- intégrité du package BeltOut autoritaire.

L'intake produit dans le dossier privé :

- `frozen-intake.json` ;
- `FREEZE.lock` ;
- `conversion-plan.json` ;
- les 12 prises brutes retenues sous `raw-selected/`.

Le gel peut être revérifié avant conversion :

```bash
python tools/p6_s15_pipeline.py verify-frozen <DOSSIER_PRIVE>/frozen-intake.json
```

Toute dérive de hash après gel est bloquante.

Le plan généré impose déjà :

- seed `202609060000 + segment` ;
- conversion ordinal `1` uniquement ;
- aucun retry après existence d'une sortie audio ;
- aucun best-of-N ;
- aucun second pass ;
- `constant_level_alignment_only` comme seul traitement post-conversion.
