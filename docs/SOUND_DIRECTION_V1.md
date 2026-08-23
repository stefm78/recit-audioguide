# Sound Direction v1

La direction sonore appartient au projet éditorial (`recit-audioguide`), pas à `audio-engine`.

`audio-engine` réalise fidèlement un programme audio. Cette couche décide **pourquoi** un son, une voix, un silence ou un espace mérite l’attention avant de produire le programme v6.

## Règle d’or

> L’auditeur doit suivre l’histoire, pas remarquer le moteur.

## Grammaire minimale

Pour chaque beat narratif, le directeur sonore décide :

1. **attention_owner** — qui ou quoi doit être au premier plan : `voice`, `sound`, `silence`, `space` ;
2. **purpose** — ce que ce beat apporte : installer, interrompre, révéler, faire attendre, déplacer, relâcher, conclure ;
3. **voice_state** — intention de diction de la réplique : projetée, nerveuse, intime, retenue, ralentie, etc. ;
4. **background** — uniquement les couches qui ont une raison narrative de rester présentes ;
5. **handoff** — si l’attention passe de la voix au son ou du son à la voix ;
6. **exit** — comment le beat disparaît : coupure motivée, fondu, carry sous la parole ou silence.

Le directeur exprime une intention relative. Il ne doit pas inventer des millisecondes quand la durée réelle de la diction peut servir d’autorité.

## Contraintes éditoriales

- **Show, don’t tell sonore** : ne pas faire dire au narrateur ce qu’un son immédiatement intelligible raconte déjà.
- **Une couche, une raison** : aucune texture continue n’est ajoutée uniquement parce que le moteur sait la mixer.
- **Un propriétaire principal de l’attention par beat** : plusieurs couches peuvent coexister, mais une seule doit dominer perceptivement.
- **Le silence est un choix positif** : ne jamais combler automatiquement un espace.
- **La diction appartient à la réplique** : un même personnage peut changer de rythme, de projection et de proximité sans changer artificiellement de voix.
- **Le son historique est une évocation documentée** : provenance et licence sont tracées ; une évocation ne devient pas une preuve historique.
- **Mesure > estimation** : après TTS, les durées audio mesurées pilotent l’assemblage.
- **Préview avant batch** : les scènes sensibles sont écoutées via le fast preview avant la validation globale.

## Niveaux d’attention

| Niveau | Usage | Réalisation typique |
|---|---|---|
| `texture` | sentir sans remarquer | bed/layer fortement en retrait |
| `punctuation` | remarquer un événement | événement bref |
| `foreground` | écouter le son à la place du narrateur | `scene` |
| `handoff` | revenir progressivement à la voix | `bridge` + carry relatif |
| `silence` | créer attente ou contraste | pause assumée |

## Critère Gold Master

Un morceau de référence est réussi si :

- aucune phrase n’explique inutilement un effet sonore évident ;
- chaque couche peut justifier son existence en une phrase ;
- les personnages ont une petite trajectoire émotionnelle perceptible ;
- au moins un moment laisse le son raconter seul ;
- la reprise de voix après un climax sonore paraît naturelle ;
- retirer un effet inutile améliore plutôt que dégrade la scène ;
- aucune sophistication DSP n’est nécessaire pour comprendre la mise en scène.

La sortie de cette couche reste un programme `audio-engine` v6. Aucun nouveau repo ni service n’est requis à ce stade.
