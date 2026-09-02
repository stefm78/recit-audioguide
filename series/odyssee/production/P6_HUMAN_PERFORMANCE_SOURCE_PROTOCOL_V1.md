# P6 — Ulysse — protocole de performance humaine source V1

## Statut

Hypothèse autorisée pour fermer le dernier gate critique de Stream 2 :

`performance humaine française -> BeltOut -> identité Henri/Ulysse -> reconstruction P6 -> human review`

Cette hypothèse remplace les cellules TTS monolithiques et les chaînes VoiceDesign/CosyVoice3 déjà closes.

## Principe scientifique

La performance humaine fournit uniquement :

- rythme ;
- respiration ;
- intention ;
- retenue ;
- émotion ;
- naturel du français.

BeltOut fournit uniquement le timbre cible Henri/Ulysse.

Le comédien source n'a donc pas besoin de ressembler vocalement à Henri. Une voix masculine adulte est préférable afin de limiter les transformations extrêmes de registre.

## Qualification — cinq prises exactes

Une seule prise gelée par ligne est remise au pipeline.

| ID | Texte exact | Durée H1b-B de référence | Fenêtre visée à l'enregistrement |
|---|---|---:|---:|
| 02 | `Non.` | 1.776 s | environ 1.4–2.1 s |
| 04 | `Ce lit ne sort pas de cette chambre.` | 2.688 s | environ 2.2–3.2 s |
| 10 | `Tu le savais.` | 1.776 s | environ 1.4–2.1 s |
| 12 | `Pénélope…` | 1.776 s | environ 1.4–2.1 s |
| 15 | `Notre lit.` | 1.776 s | environ 1.4–2.1 s |

Les durées sont des guides de jeu, pas des objectifs à atteindre par montage.

## Direction commune

Ulysse n'est pas en train de faire un discours.

Il est dans sa propre maison, face à une femme qu'il aime et qu'il n'a pas vue depuis vingt ans. Elle met à l'épreuve la seule chose qu'aucun imposteur ne devrait connaître : le lit construit autour d'un olivier vivant.

Direction générale :

- jouer proche, intime, presque comme si Pénélope était à un mètre ;
- aucune grandeur héroïque ;
- aucune voix de bande-annonce ;
- aucune déclamation ;
- émotion réelle mais retenue ;
- ne pas chercher à "faire triste" ;
- laisser le sens provoquer la respiration ;
- parler un français quotidien et naturel ;
- ne pas allonger artificiellement les voyelles ;
- pas de chuchotement systématique ;
- pas de sanglot ;
- pas de cri.

## Direction ligne par ligne

### 02 — `Non.`

**Fonction :** le corps réagit avant l'intelligence.

Ce n'est pas une réponse argumentée. Ulysse vient d'entendre quelque chose d'impossible : déplacer le lit.

**Jeu :**

- refus réflexe ;
- choc bas, immédiat ;
- souffle court possible juste avant ou juste après ;
- volume contenu ;
- le mot peut presque tomber plutôt qu'être projeté.

**À éviter :**

- colère ;
- cri ;
- `Nooon !` prolongé ;
- effet tragique.

### 04 — `Ce lit ne sort pas de cette chambre.`

**Fonction :** après le choc, la certitude.

Ulysse sait quelque chose que seul celui qui a construit le lit peut savoir.

**Jeu :**

- ferme sans hausser la voix ;
- précision ;
- tension intime ;
- la certitude doit être plus forte que la colère ;
- laisser une petite respiration naturelle entre `lit` et la suite uniquement si elle vient spontanément.

**À éviter :**

- démonstration ;
- menace ;
- récitation solennelle.

### 10 — `Tu le savais.`

**Fonction :** le basculement.

Ce n'est plus l'accusation `tu aurais dû le savoir`. Il comprend qu'elle savait, qu'elle vient de le reconnaître et qu'il vient lui-même de comprendre son test.

**Jeu :**

- reconnaissance bouleversée mais contenue ;
- soulagement mêlé d'une ancienne blessure ;
- moins de projection qu'à la ligne 04 ;
- une légère fragilité est bienvenue si elle arrive naturellement.

**À éviter :**

- pleurer la phrase ;
- insister théâtralement sur `toi` ou `savais` ;
- fabriquer une voix cassée.

### 12 — `Pénélope…`

**Fonction :** pour la première fois, le nom n'est plus une tentative de convaincre.

Il la reconnaît à nouveau comme sa femme.

**Jeu :**

- très simple ;
- intime ;
- étonnement doux ;
- le silence après le nom compte davantage que l'allongement du nom.

**À éviter :**

- chuchoter ;
- traîner les syllabes ;
- faire une déclaration d'amour.

### 15 — `Notre lit.`

**Fonction :** résolution intime.

Le mot important est `notre`, mais il ne doit pas être surligné. Le lit est la preuve matérielle de leur histoire commune.

**Jeu :**

- chaleur grave ;
- soulagement ;
- certitude retrouvée ;
- presque plus simple que les lignes précédentes ;
- fin naturelle, sans effet de fermeture.

**À éviter :**

- pathos ;
- sourire audible forcé ;
- accentuation démonstrative de `notre`.

## Surface Web recommandée

Utiliser en priorité :

`web/reviews/odyssee-p6-human-performance.html`

Cette surface :

- affiche le dialogue H1b-B complet et les répliques de Pénélope ;
- permet d'écouter la scène complète et le contexte immédiat de chaque ligne ;
- demande l'autorisation microphone uniquement à l'utilisateur ;
- conserve tous les essais localement dans IndexedDB ;
- permet de retenir exactement une prise par ligne ;
- exporte uniquement les cinq prises retenues dans un ZIP avec manifeste et SHA-256 ;
- n'effectue aucun upload automatique.

## Procédure d'enregistrement

### Avant le gel

Le comédien peut :

- lire le contexte ;
- répéter autant que nécessaire ;
- refaire des prises ;
- écouter ses propres répétitions ;
- ajuster son interprétation.

Cette phase n'est pas une expérience machine.

### Au moment du gel

Choisir **une seule prise par ligne avant toute conversion BeltOut**.

Fichiers attendus :

- `02-non.wav`
- `04-ce-lit.wav`
- `10-tu-le-savais.wav`
- `12-penelope.wav`
- `15-notre-lit.wav`

Une fois ces cinq fichiers remis à Stream 2 :

- leurs SHA-256 sont gelés ;
- aucune autre prise ne peut les remplacer après écoute d'une sortie BeltOut ;
- un seul passage BeltOut par ligne est autorisé.

## Qualité d'enregistrement

Préféré :

- WAV PCM ;
- mono ;
- 44.1 ou 48 kHz ;
- 16 ou 24 bits ;
- pièce calme ;
- bouche à environ 15–30 cm du micro ;
- niveau sans saturation.

Acceptable pour le gate :

- enregistrement smartphone propre ;
- M4A/MP3 non saturé, qui sera converti de façon déterministe avant BeltOut.

Éviter :

- réduction de bruit agressive ;
- réverbération ajoutée ;
- compresseur/auto-level audible ;
- pitch correction ;
- changement de vitesse ;
- musique ou ambiance ;
- coupure à ras du premier ou dernier phonème.

Laisser environ 200–500 ms de silence naturel avant et après la phrase si possible.

## Gate machine après réception

Pour chaque prise gelée :

1. intégrité + SHA-256 ;
2. audio fini, non silencieux, non saturé ;
3. durée raisonnable ;
4. exactement une conversion BeltOut vers l'anchor Henri/Ulysse ;
5. conservation de durée source ;
6. déplacement du timbre vers Henri ;
7. reconstruction de la scène P6 sans modifier Pénélope, les pauses ou les éléments non ciblés.

Si une prise échoue uniquement pour une incompatibilité technique du fichier, une normalisation de conteneur/codec est permise ; aucune correction artistique n'est permise après gel.

## Gate humain final

Le candidat passe uniquement si :

- impact >= 4/5 ;
- reaction PASS ;
- identity PASS ;
- french PASS ;
- melodrama NONE ;
- staging PASS.

Un PASS émet `ULYSSES_EMOTIONAL_HUMAN_PASS` et permet à Stream 2 de sortir du chemin critique.

## Après qualification

Le test porte sur les cinq lignes condensées de P6. Le binding produit S15 reste distinct et contient plusieurs segments Ulysse réels.

Un PASS qualifie la **capability** `human-performance -> BeltOut -> Henri/Ulysse`. La matérialisation des segments S15 exacts pourra ensuite reprendre le même protocole sous Stream 3 sans rouvrir la recherche de modèle.
