# Processus artistique — audit de composition narrative

Autorité : issue #76 — ART-WP-002.

## But

Maximiser la richesse perçue d’un récit long sans transformer l’œuvre en catalogue documentaire, sans sur-expliquer et sans optimiser acoustiquement un texte qui n’est pas encore figé.

La revue porte sur la **composition narrative**, pas sur un quota d’ingrédients.

## Les sept familles

1. **Moteur dramatique**
   - action ;
   - obstacle ;
   - décision ;
   - conséquence ;
   - suspense ;
   - révélation.

2. **Personnages et relations**
   - désir ;
   - peur ;
   - contradiction ;
   - passé utile ;
   - évolution ;
   - relation et rapport de pouvoir.

3. **Monde et civilisation**
   - lieux ;
   - objets ;
   - vêtements ;
   - nourriture ;
   - coutumes ;
   - rites ;
   - organisation sociale ;
   - pouvoir ;
   - croyances ;
   - économie domestique.

4. **Expérience sensorielle**
   - espace ;
   - matière ;
   - lumière ;
   - température ;
   - faim ;
   - fatigue ;
   - odeur ;
   - mouvement ;
   - silence.

5. **Sens et motifs**
   - thèmes ;
   - symboles ;
   - motifs récurrents ;
   - échos ;
   - préparation et payoff.

6. **Orientation narrative**
   - temps ;
   - lieu ;
   - causalité ;
   - identité ;
   - changement de propriétaire du récit ;
   - information minimale nécessaire.

7. **Rythme et expérience audio**
   - alternance narration/dialogue ;
   - respiration ;
   - tension ;
   - silence ;
   - densité ;
   - potentiel sonore ;
   - variation des plaisirs narratifs.

## Les quatre questions

Pour chaque ingrédient :

- **Présence** — existe-t-il lorsque la scène en a besoin ?
- **Qualité** — est-il crédible, précis et utile ?
- **Dosage** — est-il trop faible, juste ou envahissant ?
- **Placement** — arrive-t-il au bon moment ?

Une absence n’est pas un défaut si elle est cohérente avec la fonction de la scène.

## Échelle d’intégration de l’information

Préférence générale :

1. **vécue / dramatisée** ;
2. **montrée** ;
3. **dite naturellement par un personnage** ;
4. **expliquée par la narration**.

Cette échelle n’interdit pas l’exposition. Elle oblige à justifier son coût.

## Scoring

Les scores sont des **jugements éditoriaux comparatifs**, pas des mesures scientifiques.

Échelle 1–5 :

- 1 : défaut sévère ;
- 2 : insuffisant ;
- 3 : fonctionnel mais faible ;
- 4 : solide ;
- 5 : excellent / exemplaire.

Pondération pour le métascore après exclusion des blockers :

- moteur dramatique : 25 % ;
- personnages & relations : 15 % ;
- monde & civilisation : 15 % ;
- sensoriel : 10 % ;
- sens & motifs : 10 % ;
- orientation : 10 % ;
- rythme & audio : 15 %.

## Critères non compensables

Un métascore élevé ne masque jamais :

- incohérence importante ;
- confusion temporelle ou narrative ;
- exposition artificielle majeure ;
- anachronisme important ;
- personnage essentiel insuffisamment construit ;
- scène longue sans fonction ;
- information nécessaire absente ;
- payoff essentiel non préparé ;
- changement de narrateur incompréhensible.

Un seul défaut sérieux peut produire **HOLD**.

## Gates

### N0 — audit sans modification

- lire l’œuvre complète ;
- cartographier les sept familles ;
- relever les forces, manques, excès, répétitions et zones volontairement légères ;
- ne modifier aucune ligne du récit.

Sortie : diagnostic.

### N1 — challenge contradictoire du diagnostic

Chaque alleged gap doit survivre à la question :

> Est-ce réellement un défaut, ou seulement quelque chose que l’on pourrait ajouter ?

Rejeter toute amélioration qui :

- n’apporte qu’une information intéressante mais non nécessaire ;
- casse la tension ;
- transforme le monde vécu en cours ;
- répète un motif déjà compris ;
- exige plusieurs phrases pour justifier une seule phrase ajoutée.

Sortie : diagnostic nettoyé.

### N2 — sélection minimale

Classer les changements survivants :

- **A** — correction structurante / importante ;
- **B** — enrichissement chirurgical à fort rendement ;
- **C** — ne pas toucher.

Seuls A et B sont autorisés.

### N3 — revue post-révision

Relire le texte révisé sans utiliser la justification des changements comme argument.

Chercher :

- lourdeur nouvelle ;
- répétition ;
- exposition ;
- perte de rythme ;
- déplacement d’un climax ;
- rupture de voix ;
- effet domino non prévu.

Si les modifications améliorent le texte sans créer de nouveau défaut matériel : **NARRATIVE_FREEZE**.

Sinon : retour ciblé en N2.

## Dream Team et légitimité

L’arbitre dépend du problème :

- structure, climax, tension : dramaturgie ;
- Homère, motifs et architecture : narratologie / études homériques ;
- civilisation, coutumes, objets : histoire / anthropologie ;
- oralité française : direction de texte ;
- écoute : réalisation audio ;
- complexité du processus : gouvernance fail-cheap ;
- résultat final : auditeur.

Pas de vote moyen. L’expertise la plus légitime arbitre la question concernée.

## Human gate policy

L’humain n’est pas requis pour confirmer :

- un tableau ;
- un JSON ;
- un diagnostic textuel raisonnablement objectivable ;
- une CI verte.

L’humain devient indispensable lorsque la question est réellement perceptuelle :

- identité de voix ;
- naturel du jeu ;
- compréhension d’un handoff narratif à l’oreille ;
- immersion ;
- fatigue / envie de continuer sur la durée ;
- verdict final du master.

## Coordination avec la production audio

Règle :

> Le texte long doit être audité puis figé avant optimisation audio approfondie.

Exception :

un probe audio peut continuer avant freeze s’il valide un invariant qui reste pertinent quelle que soit la révision textuelle.

Pour l’Odyssée :

- P1 : PASS acquis ;
- P2 : pertinent, car il valide la grammaire narratrice → Ulysse ;
- P3–P6 : HOLD jusqu’au freeze narratif ;
- aucun master long avant freeze.

## Règle d’arrêt

Lorsque deux challenges successifs n’identifient plus de défaut matériel et ne produisent que des préférences stylistiques contradictoires :

**STOP TUNING → FREEZE.**

Le but est de finir une œuvre robuste, pas de conserver un atelier éternel.
