# Stratégie de casting — L’Odyssée

## Autorité technique

Consumer Audio Engine pin :

3392d4f22f0a9b054a05b5c05a7856985c0ab030

Le catalogue validé contient notamment quatre voix adultes sous-jacentes :

- fr-FR-RemyMultilingualNeural ;
- fr-FR-HenriNeural ;
- fr-FR-DeniseNeural ;
- fr-FR-VivienneMultilingualNeural.

Les presets fournissent plusieurs performances, mais un preset différent utilisant la même provider voice ne constitue pas automatiquement une nouvelle identité vocale.

## Priorité

identité du rôle central > naturel du français > performance > quantité de voix distinctes.

## Noyau à protéger

Les rôles suivants doivent être immédiatement distinguables sur une écoute longue :

1. narratrice ;
2. Ulysse ;
3. Pénélope ;
4. Télémaque.

Athéna est également importante, mais peut être différenciée par une combinaison de voix, performance et rareté sans devenir une cinquième voix omniprésente.

## Candidats — non gelés

Cette matrice sert à sélectionner des probes, pas à déclarer le casting final.

| Rôle | Besoin | Candidats validés actuels |
|---|---|---|
| narratrice | chaleur, continuité 80 min, retrait possible | conteuse-chaleureuse |
| Ulysse | adulte, autorité souple, narration longue | marin-bourru ; erudit-solennel ; narrateur-vif à ralentir |
| Pénélope | adulte, intelligence, autorité sans dureté | aristocrate-distante ; conteuse-chaleureuse ; messagere-adulte-denise à ralentir |
| Télémaque | jeune adulte masculin, énergie contrôlée | narrateur-vif ; soldat-jovial fortement retenu |
| Athéna | calme, précision, autorité | aristocrate-distante ; femme-mysterieuse |
| Calypso | chaleur / assurance | conteuse-chaleureuse ; femme-mysterieuse |
| Nausicaa | jeune adulte naturelle | messagere-adulte-denise ; messagere-adulte-vivienne |
| Polyphème | masse / lenteur / français intact | officier-autorite ; homme-age-sage |
| Euryloque | marin concret | marin-bourru |
| Circé | autorité calme | aristocrate-distante ; femme-mysterieuse |
| Tirésias | âge / calme | homme-age-sage |
| Anticlée | âge / chaleur | ancienne-memoire |
| Antinoos | assurance / domination | notable-hautain ; officier-autorite |
| Eurymaque | autorité secondaire | erudit-solennel ; notable-hautain |
| Eumée | chaleur directe | marin-bourru ; soldat-jovial retenu |
| Euryclée | âge / chaleur | ancienne-memoire |

## Problème connu

Le noyau narratrice / Pénélope / Athéna / Calypso / Circé / Nausicaa dépasse le nombre de provider voices féminines adultes validées.

Il serait mauvais de résoudre cela par six variations extrêmes de la même voix.

## Décision

Ne pas ouvrir Audio Engine.

Avant le casting final, effectuer une étape de découverte/casting Production :

1. vérifier les voix fr-FR réellement disponibles au provider Edge au moment du probe ;
2. privilégier les voix françaises dédiées pour les ancrages lorsque possible ;
3. générer seulement des probes courts sur les rôles à collision ;
4. choisir une distribution de type audiobook avec doublage contrôlé des rôles éloignés.

## Doublage possible

Exemples de doublage à tester, pas à imposer :

- même actrice pour Calypso et Euryclée : mauvais, trop éloigné en âge ;
- même actrice pour Nausicaa et une petite voix de foule : acceptable ;
- même acteur pour Polyphème et Tirésias : possible si les séquences sont éloignées et les performances naturelles ;
- même acteur pour Antinoos et un roi phéacien : possible ;
- même acteur pour Eumée et Euryloque : risqué car deux rôles masculins chaleureux proches de l’arc d’Ulysse.

## Gate de casting futur

Aucun casting central n’est gelé avant un probe contenant au minimum :

- narratrice → Ulysse conteur ;
- Ulysse / Télémaque ;
- Ulysse / Pénélope ;
- Pénélope / Athéna ;
- Nausicaa ;
- Polyphème.

Le probe doit tester l’identité, le français et la fatigue potentielle, pas seulement une phrase spectaculaire.
