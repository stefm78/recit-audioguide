# Format de série

Chaque collection vit dans `series/<slug>/series.json`.

Champs obligatoires :
- `schema_version`: actuellement `1`.
- `slug`: identifiant stable.
- `type`: `story`, `visit` ou `route`.
- `title`.
- `episodes`: liste ordonnée.

Chaque épisode exige `id` et `title`. Le reste est progressif :
- `audio_url`: audio déjà disponible, local ou distant.
- `source_file`: script JSON local à rendre avec le moteur audio.
- `summary`, `stop`, `launch`, `look`, `maps_url`, `transcript_url` sont facultatifs.
- `extras` contient des capsules facultatives.

Si `source_file` et `audio_url` existent ensemble, `audio_url` sert de repli : un échec de rendu ne bloque pas la publication.

## Script audio

Un `source_file` contient au minimum :
```json
{
  "id": "serie-ep01",
  "title": "Titre",
  "segments": [
    {"speaker": "Narrateur", "preset": "narrateur-vif", "text": "..."}
  ]
}
```

## Qualité

Bloquant : manifeste invalide, type inconnu, épisode sans identifiant ou titre.

Avertissement : audio absent, résumé absent, repère de lancement absent en mode route, média secondaire indisponible.
