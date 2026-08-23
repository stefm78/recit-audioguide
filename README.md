# Récit audioguide

Compagnon de voyage audio statique, simple et résilient.

## Principes

- L'histoire d'abord.
- Trois modes seulement : `story`, `visit`, `route`.
- Une nouvelle série est du contenu, pas du code.
- L'enrichissement sonore suit d'abord l'époque racontée : sons physiquement plausibles pour le sujet, sans bruit moderne par défaut et sans prétendre à une reconstitution authentique.
- Quand un son porte suffisamment d'information ou d'émotion, le récit peut lui céder brièvement la scène ; transitions et fades restent doux par défaut.
- Le design sonore exprime aussi le transfert d'attention : son sous la voix, son seul, reprise de la voix avec le son qui s'efface, ou accent acoustique bref.
- Un accent acoustique doit rester court : on découpe une phrase signifiante plutôt que de laisser un effet de réverbération sur une longue narration.
- Les espaces acoustiques servent l'immersion sans sacrifier l'intelligibilité et restent des évocations, jamais une fausse reproduction acoustique d'un lieu nommé.
- Le site reste utilisable si les enrichissements secondaires échouent.
- On bloque uniquement ce qui rend l'expérience fausse, inutilisable ou dangereuse.
- Aucun backend permanent, aucune base de données, aucun compte utilisateur.

## Architecture

- `series/` : manifestes, scripts audio et assets propres aux séries.
- `site/` : validation légère et construction du site statique.
- `web/` : shell Web commun.
- `.github/workflows/` : appel du moteur audio partagé puis publication GitHub Pages.

La synthèse, le casting de voix, la normalisation et l'assemblage audio appartiennent au dépôt indépendant `stefm78/audio-engine`. Récit audioguide est un **client** de ce moteur et ne contient aucun code TTS.

Les scripts audio restent dans ce dépôt parce qu'ils font partie du contenu éditorial. Le moteur reçoit ces scripts, produit les assets audio et leurs manifestes, puis le site les consomme. Les URLs audio historiques restent des fallbacks pendant la migration.

Le dépôt historique `stefm78/audioguide` reste la source de migration tant que la parité n'est pas atteinte.
