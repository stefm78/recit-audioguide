# Human perceptual review batching

Authority: #93 — ART-WP-003.

## Goal

Reduce human review overhead without weakening causal diagnosis.

The system prepares independent probes in parallel and groups them into bounded human listening sessions.

## Core rule

> Serialize only true dependencies, not humans.

A human batch is a shared review surface, not a shared verdict.

Each module keeps:
- its own immutable candidate;
- its own audio digest;
- its own criteria;
- its own PASS / FAIL;
- its own promotion decision.

No weighted average or majority vote can compensate for a failed critical module.

## Batch design

A useful batch should:
- contain 2–5 independent perceptual modules;
- stay within a bounded listening session, typically 3–10 minutes;
- avoid repeating the same question under different labels;
- expose only machine-PASS candidates;
- produce one copyable consolidated report;
- allow a reviewer to stop and resume without losing state.

## Odyssée batches

### H1 — critical artistic risks

Prepare in parallel:

1. **P4 — Siren**
   - new provider/capability candidate;
   - attraction;
   - natural French;
   - no cliché;
   - preserve validated P4 v3 dialogue architecture.

2. **P5 — Underworld**
   - minimal-layer strangeness;
   - Ulysses / Anticlea emotional contact;
   - no heavy reverb;
   - re-check the P2 watch: “Ulysse pas assez conteur”.

3. **P6 — bed**
   - Penelope/Ulysses recognition;
   - emotional climax without music;
   - pauses and text carry the scene;
   - no overacting.

H1 publishes only when all included modules have immutable machine-PASS candidates.

A failure in P4 does not invalidate P5/P6 and vice versa.

### H2 — block integration

After critical probe promotions:
- representative block joins;
- pacing/fatigue;
- narrator ↔ character handoffs;
- sound-density consistency;
- loudness/space continuity.

H2 should prefer longer integrated excerpts over many isolated micro-probes.

### H3 — final master

One continuous long-form listen.

Questions:
- desire to continue;
- fatigue;
- identity stability;
- global rhythm;
- emotional climax;
- moments where the listener notices the production mechanism.

## Human-effort rule

Do not create a new human page if:
- the new question can be added to an upcoming batch without losing causality;
- the candidate can be prepared in parallel;
- no human decision is needed to continue machine work.

Create a standalone human page only when:
- a blocking decision is urgent and no other independent tests can reasonably be prepared;
- or the perceptual task would contaminate another test if grouped.

## Fail-cheap rule

Machine failures are resolved before the human batch is published.

Human reviewers never confirm:
- schema;
- file presence;
- CI;
- hashes;
- unsupported provider names;
- deterministic routing.

## Review output

One consolidated copyable report with separate sections:

- P4 verdict;
- P5 verdict;
- P6 verdict;
- cross-cutting notes.

Promotions remain independent.

## Stop rule

If a module fails, continue preparing independent modules.

Do not force the reviewer back into a one-page/one-loop cadence unless a true dependency requires it.
