# Probes de risque — L’Odyssée

## Objectif

Tester les risques qui pourraient rendre 85 minutes inutilisables avant de produire 85 minutes.

Les probes ne sont pas des bandes-annonces.

## P0 — cheap only

Aucun TTS.

Vérifier :

- sources de texte présentes ;
- droits/source lane ;
- casting candidates résolus ;
- Program schema valide lorsque le Program existera ;
- capabilities demandées supportées ;
- assets requis identifiés ;
- aucun champ artistique silencieusement perdu.

Gate : PASS obligatoire.

## P1 — identité centrale

Durée cible : 60–90 secondes.

Contenu original spécifique au probe :

- narratrice ;
- Ulysse ;
- Télémaque ;
- Pénélope ;
- Athéna.

Doit contenir de courtes alternances, pas cinq monologues séparés.

Questions :

- qui parle sans regarder le texte ?
- Ulysse et Télémaque se distinguent-ils immédiatement ?
- Pénélope et Athéna se distinguent-elles ?
- français intact ?
- aucune voix enfantine involontaire ?

Machine : technique/timing.

Humain : uniquement si plusieurs castings machine-admissibles restent à départager.

## P2 — propriété du récit

Durée cible : 45–75 secondes.

Moment :

- narratrice décrit l’étranger chez les Phéaciens ;
- question sur son identité ;
- Ulysse dit son nom ;
- Ulysse commence à raconter le Cyclope.

Objectif :

faire entendre le changement narratrice → Ulysse sans jingle ni explication.

Gate perceptuel futur : transition naturelle.

## P3 — Polyphème

Durée cible : 30–45 secondes.

Contient :

- Ulysse ;
- Polyphème ;
- un marin.

Objectif :

- masse et menace ;
- français de Polyphème intact ;
- aucune caricature DSP ;
- Ulysse reste identifiable.

## P4 — Sirènes

Durée cible : 30–45 secondes.

Contient :

- Ulysse ;
- Sirène(s) ;
- coque/cordage si assets qualifiés.

Objectif :

- voix intelligible ;
- attirante sans cliché ;
- attention qui se resserre ;
- pas de surcharge.

## P5 — Enfers

Durée cible : 30–60 secondes.

Contient :

- Ulysse ;
- Anticlée ou Tirésias.

Objectif :

prouver qu’une scène peut être étrange avec très peu de couches.

Gate :

si l’effet repose sur une réverbération lourde, FAIL direction artistique.

## P6 — lit

Durée cible : 45–60 secondes.

Contient :

- Pénélope ;
- Ulysse.

Aucune musique requise.

Objectif :

vérifier que la reconnaissance finale tient par le jeu, les pauses et le texte.

## Sélection fail-cheap

Premier cycle TTS :

P1 + P2 seulement.

Si P1 échoue : ne pas produire P3–P6.

Si P1 PASS mais P2 échoue : corriger casting/performance/handoff avant les probes de monde sonore.

P3–P6 seulement après identité centrale stabilisée **et après `NARRATIVE_FREEZE` du processus ART-WP-002**.

Statut Odyssée au 2026-08-30 :

- P1 : PASS humain promu ;
- P2 : **PASS humain**, clarté 4/5, propriété Ulysse PASS, transition naturelle PASS ;
- P2 watch non bloquant : Ulysse perçu « pas assez conteur » ; préserver l’identité P1 et réévaluer sur les probes/assemblages suivants sans retuning spéculatif ;
- NARRATIVE_FREEZE : PASS après N3 ;
- P3 : **AUTHORIZED** ;
- P4–P6 : séquencés après P3 selon leur propre gate ;
- master long : **HOLD_CRITICAL_PROBES**.

## Human gate policy

Le premier humain n’intervient pas pour confirmer un JSON.

Il intervient seulement si :

- plusieurs castings techniquement admissibles exigent une préférence perceptuelle ;
- ou un probe réellement audio doit être jugé pour naturel/immersion.

Aucune écoute de l’œuvre complète avant le master long.
