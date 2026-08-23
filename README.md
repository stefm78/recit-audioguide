# Récit audioguide

Compagnon de voyage audio statique, simple et résilient.

## Principes

- L'histoire d'abord.
- Trois modes seulement : `story`, `visit`, `route`.
- Une nouvelle série est du contenu, pas du code.
- Le site reste utilisable si les enrichissements secondaires échouent.
- On bloque uniquement ce qui rend l'expérience fausse, inutilisable ou dangereuse.
- Aucun backend permanent, aucune base de données, aucun compte utilisateur.

## Architecture cible

- `series/` : manifestes et épisodes.
- `engine/` : validation, génération audio et construction du site.
- `web/` : shell Web commun.
- `.github/workflows/` : pipeline générique et publication GitHub Pages.

Le dépôt historique `stefm78/audioguide` reste la source de migration tant que la parité n'est pas atteinte.
