# Principes de gouvernance produit

## Steve
- L’histoire est le produit ; l’interface s’efface.
- Une action principale par écran : écouter.
- Aucun détail de production visible au voyageur.
- Toute fonction doit justifier la complexité qu’elle ajoute.

## Linus
- Une nouvelle série ne crée ni code ni workflow.
- Le format de contenu est stable, lisible et versionné.
- Les erreurs secondaires dégradent ; elles ne bloquent pas la publication.
- Pas de dépendance serveur lorsque le Web statique suffit.

## Comité d’experts
- Exactitude historique : bloquer seulement une erreur critique connue.
- Audio : mauvaise langue persistante, fichier absent ou inutilisable = bloquant pour l’épisode concerné, pas pour toute la série.
- Sécurité route : aucune incitation visuelle destinée au conducteur en mouvement.
- Accessibilité : navigation clavier, grands contrôles tactiles, transcription disponible lorsque possible.

## Règle de livraison
Le pipeline publie tout ce qui est utilisable. Les avertissements sont consignés dans `build-report.json` sans empêcher la sortie.
