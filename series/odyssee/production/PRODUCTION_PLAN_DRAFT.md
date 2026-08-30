# Production Plan éditorial — draft

## Statut

Ce document précède le Program Audio Engine.

Il contient des décisions de production et ne doit pas copier les futurs champs bas niveau juste pour ressembler au renderer.

## Identité

- product : audiobook / récit immersif long-form ;
- work_id : odyssee ;
- unit_id : odyssee-longform-v1 ;
- language : fr-FR ;
- duration_target : 75–90 min ;
- continuity_scope : œuvre complète ;
- sound_density : scene-rich-but-selective ;
- narrator_policy : narratrice externe + bascule longue vers Ulysse conteur.

## Objectif

Faire vivre le retour d’Ulysse comme une transformation de l’identité : être absent, se nommer, devenir Personne, perdre les autres, revenir sous masque, être reconnu.

## Hiérarchie des priorités

### ESSENTIAL

- intelligibilité du français ;
- identité Ulysse ;
- identité Pénélope ;
- identité Télémaque ;
- distinction narratrice / Ulysse conteur ;
- causalité narrative ;
- séquence finale du lit ;
- toutes les répliques nécessaires à la compréhension.

Une impossibilité sur un élément ESSENTIAL bloque avant commitment si elle est détectable.

### IMPORTANT

- Athéna identifiable ;
- Euryloque récurrent ;
- transitions de propriétaire narratif ;
- réduction perceptible de l’équipage ;
- scènes Argos et cicatrice ;
- états sonores distincts de la mer.

Un élément IMPORTANT manquant doit être corrigé avant master long, mais peut permettre un probe technique.

### SUPPORTIVE

- sons de coque ;
- cordage ;
- feu ;
- moutons ;
- détails de repas ;
- événements domestiques secondaires.

Peut être omis avec warning si la scène reste compréhensible et immersive.

### OPTIONAL

- musique ;
- textures supplémentaires ;
- bruit animal d’Argos ;
- ponctuations décoratives.

Absence préférable à un mauvais asset.

## Casting continuity

Noyau :

- narratrice ;
- Ulysse ;
- Pénélope ;
- Télémaque ;
- Athéna.

Récurrents :

- Euryloque ;
- Eumée ;
- Euryclée ;
- Antinoos.

Les autres rôles peuvent utiliser un doublage contrôlé.

Le casting final reste UNRESOLVED jusqu’aux probes.

## Performance intent

Le Production Plan retiendra des intentions sémantiques par beat/segment, notamment :

- guiding ;
- weary ;
- controlled-stranger ;
- storyteller ;
- cunning ;
- pride-burst ;
- command-under-loss ;
- contained-grief ;
- disguised-restraint ;
- testing ;
- recognition-release.

Ces intentions ne deviennent pas automatiquement des paramètres TTS.

## Fallback policy

- essential_speech : fail ;
- core_identity_conflict : fail-before-long-render ;
- supportive_sound : omit-and-warn ;
- optional_music : continue-without ;
- decorative_effect : continue-without ;
- unavailable_nonessential_asset : omit-and-warn.

## Risk hints

- core-voice-identity ;
- narrator-to-ulysse-handoff ;
- ulysse-disguised-continuity ;
- polyphème-french-integrity ;
- sirens-intelligibility ;
- underworld-low-density ;
- crew-loss-continuity ;
- bed-scene-restraint.

## Product context

- book_id : odyssee-original-adaptation ;
- part_id : longform-v1 ;
- chapter_id : continuous-work ;
- continuity_scope : work ;
- sound_density : selective ;
- narrator_pace_policy : stable-long-form-with-owned-flashback ;
- assembly_id : odyssee-longform-v1.

## Commit point

Le long render n’est autorisé qu’après :

1. prose complète ;
2. cheap validation ;
3. core casting probe PASS ;
4. sound-risk probe PASS ;
5. Program preflight PASS ;
6. asset provenance PASS.

Après ce point, les éléments non essentiels se dégradent de façon contrôlée plutôt que de faire échouer toute l’œuvre.
