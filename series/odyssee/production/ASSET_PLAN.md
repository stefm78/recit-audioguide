# Plan d’assets — L’Odyssée

## Principe

Ne pas constituer maintenant une bibliothèque sonore de toute la Méditerranée.

Acquérir seulement ce que les probes et les premiers blocs demandent.

## H2 — acquisition minimale exécutable

Les listes de phases ci-dessous restent une **palette de besoins possibles**, pas une liste d’achats.

Après le premier run industriel et le préflight H2, Stream 1 autorise au maximum **trois nouvelles familles d’assets** avant la revue humaine H2 :

| Stable id | Type | Usage borné | Contrainte artistique |
|---|---|---|---|
| `odyssee-strong-wind` | event | S02 tempête/rupture ; S06 ouverture du sac / renversement | rafale/vent naturel ; jamais bed marin permanent ; pas de tonnerre spectaculaire requis |
| `odyssee-wood-stress` | event | S02 radeau/bois sous contrainte ; S06 coque/destruction comprimée | craquement/contrainte de bois crédible ; bref ; pas de pas, voix ou ambiance narrative incorporée |
| `odyssee-bow-release` | event | S14 arc, ponctuation privilégiée du basculement | corde/arc sec et lisible ; pas de son assimilable à une arme à feu ; aucun effet héroïque |

Ces trois ids sont un **plafond, pas un quota**.

### Ce qui n’est pas à acquérir avant H2

Par défaut, ne pas lancer d’acquisition pour :

- mer/ressac générique ;
- corde/grément continu ;
- moutons ;
- feu ;
- pierre ;
- animaux de ferme ;
- chien Argos ;
- banquet/vaisselle ;
- textile/métier ;
- porte/pas/bois domestique ;
- impacts de combat supplémentaires.

Ces matières restent `omit-and-warn` ou silence tant qu’un rendu intégré ne démontre pas un manque narratif concret.

Cas particuliers :

- S05 peut fonctionner avec `confined-stone` + voix + silence : aucun asset pierre n’est obligatoire ;
- S06 doit surtout faire entendre la réduction de flotte par **soustraction** (moins de voix / moins de densité), pas par un mur d’effets ;
- S08 utilise le `dark_air` P5 déjà gelé et hashé ; ne pas lancer une nouvelle acquisition ;
- S09 reste principalement vocal ; ne pas acquérir une “mer des Sirènes” ;
- S13/Argos : aucun son de chien requis ;
- S15 : aucun asset requis ; le silence reste la référence.

### Acquisition autonome

Utiliser en priorité le workflow générique déjà existant :

`stefm78/audio-engine/.github/workflows/acquire-sound.yml`

Politique :

1. providers autonomes : Wikimedia Commons / Openverse en premier ;
2. un seul résultat retenu par stable id ;
3. provenance + licence + SHA-256 + sélection/catalogue conservés ;
4. publication durable en GitHub Release côté produit ;
5. aucune description comme “son authentique de la Grèce homérique” ;
6. `no-selection` n’est pas un échec de production : appliquer `omit-and-warn`, sauf si le son est devenu indispensable à la compréhension ;
7. ne jamais lancer une recherche exhaustive ou un best-of-N manuel.

### Critère d’arrêt

Une fois les trois ids ci-dessus soit qualifiés, soit explicitement omis, **l’acquisition sonore pré-H2 est terminée**.

Toute demande d’un quatrième nouvel asset doit être justifiée par un défaut perceptuel ou de compréhension observé sur un rendu intégré.

## Phase 0 — aucun asset

P1 casting et P2 changement de narrateur peuvent fonctionner presque entièrement sans asset.

C’est volontaire : si le casting central échoue, aucun travail d’acquisition ne doit avoir été gaspillé.

## Phase 1 — probes

### P3 Cyclope

Chercher au maximum :

- sheep-presence ;
- stone-mass / heavy-stone ;
- fire-hearth si utile.

Avant acquisition, tester si confined-stone + voix + silence suffisent.

### P4 Sirènes

Chercher au maximum :

- wooden-boat ;
- rope-rigging ;
- restrained-sea.

La voix reste l’élément principal.

### P5 Enfers

Aucun asset obligatoire.

### P6 Lit

Aucun asset obligatoire.

Éventuellement textile/wood uniquement si le texte et le silence ne suffisent pas.

## Phase 2 — Bloc A

Besoins probables :

- domestic-banquet-light ;
- textile / loom si réellement utile ;
- shore-surf ;
- wood-building / raft ;
- restrained-storm ;
- shore-human-light.

## Phase 3 — Bloc B/C

Besoins probables :

- ship / rigging / wind family ;
- sheep ;
- stone ;
- fire ;
- restrained-animal-presence ;
- violent-water ponctuel.

## Phase 4 — Bloc D

Besoins probables :

- domestic-interior-light ;
- hearth ;
- animal-yard ;
- bow-string ;
- door / wood ponctuel.

## Critères d’admission

Un asset doit avoir :

- provenance ;
- licence compatible ;
- hash durable ;
- source suffisamment longue pour le rôle ;
- qualité d’écoute correcte ;
- description cohérente avec l’usage.

## Pas de faux documentaire

Aucun asset ne sera décrit comme son authentique de la Grèce homérique.

Les sons sont des matériaux d’évocation.

## Fallback

Si un asset SUPPORTIVE est mauvais ou introuvable :

omit-and-warn.

Ne jamais retarder le récit pour remplir une couche décorative.
