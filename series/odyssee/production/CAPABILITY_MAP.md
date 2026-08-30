# Mapping capacités — L’Odyssée

## Runtime de référence

Consumer Audio Engine pin :

3392d4f22f0a9b054a05b5c05a7856985c0ab030

## Besoins vs capacités

| Besoin artistique | Capacité existante | Statut |
|---|---|---|
| narration sèche stable | Program v1+ | supporté |
| personnages / casting | presets / actors / character_id | supporté |
| placement simple | left / center / right | supporté |
| texture rare | bed/layers | supporté |
| événement ponctuel | punctuation | supporté |
| son seul entre deux répliques | scene | supporté |
| son puis reprise de parole | bridge | supporté |
| carry selon vraie durée TTS | v6 carry_through_segments | supporté |
| fades | bounded fades | supporté |
| ducking parole | speech ducking | supporté |
| grotte / palais / espace pierre | acoustic spaces bornés | supporté |
| extérieur ouvert | outdoor-open | supporté |
| timings exacts après TTS | timing sidecars / measured timeline | supporté |
| previews événement | preview | supporté |

## Besoins explicitement refusés

### 3D / binaural

Pas nécessaire à l’histoire.

Aucune demande Audio Engine.

### Réverbération divine personnalisée

Refusée par la direction artistique.

### Dialogues superposés

Non requis.

Les foules sont traitées par événements/texture ou paroles séquentielles.

### Automations DAW arbitraires

Non requises.

### Time-stretch musical automatique

Non requis.

### Voix de monstre DSP

Refusée.

Polyphème doit rester une voix intelligible avec mise en scène.

## Conclusion

NO_ENGINE_CHANGE.

Tout besoin actuellement identifié se place dans les capacités publiques existantes.

Une future demande moteur ne peut être ouverte que si :

1. une scène écrite exige réellement une capacité absente ;
2. aucune recette existante ne satisfait l’intention ;
3. supprimer l’effet dégraderait matériellement la scène ;
4. un changement générique est préférable à une exception Odyssée.
