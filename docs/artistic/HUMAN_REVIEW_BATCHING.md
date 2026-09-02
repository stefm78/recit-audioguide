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

### H2 — final shared block integration

The historical representative-scene scope is superseded once P4/P5/P6 capabilities are closed.

H2 now reviews the **real integrated work**, in one shared long-form structured batch:

1. Block A continuous — continuity / reference / pacing / fatigue;
2. Block B continuous — MARIN in context + P5/S08;
3. complete S09 — real P4 Sirens, two lineages, spatialization, attraction and intelligibility;
4. B→C boundary — final ~45 s of B into first ~45 s of C;
5. C→D boundary — final ~45 s of C into first ~45 s of D;
6. complete S13;
7. complete S14;
8. complete S15 — real Production Ulysse + Pénélope, never the capability probe;
9. short A/B/C/D comparison for global dynamics and inter-block levels.

Hard entry gate:

`A+B+C+D MACHINE_QUALIFIED`

H2 is not dispatched from partial review assets.

This H2 may exceed the usual 3–10 minute batch guidance because it is a long-form integration gate, not a capability-selection batch. It remains intentionally shorter and more diagnostic than H3, which is the uninterrupted final-master listen.

Authority:
- `series/odyssee/review/H2_SINGLE_BATCH_REVIEW_V1.md`;
- `series/odyssee/review/H2_SINGLE_BATCH_REVIEW_V1.json`;
- `web/reviews/odyssee-h2.html`.

There is exactly one H2. No H2a/H2b and no capability micro-review.

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

Capability batches keep independent module verdicts.

The final Odyssée H2 instead produces one consolidated integration report with:
- one neutral perceptual observation per required dimension;
- one explicit artistic PASS / FAIL per dimension;
- one final `PASS_H2_SINGLE_BATCH` or `FAIL_H2_TARGETED_CORRECTION`;
- exact immutable Release / manifest provenance.

No weighted average compensates for a failed H2 dimension.

A descriptive observation such as `melodrama PRESENT` is never itself the artistic verdict.

## Stop rule

If a module fails, continue preparing independent modules.

Do not force the reviewer back into a one-page/one-loop cadence unless a true dependency requires it.


## Review semantics — observation vs acceptance

Human-review forms must never encode artistic value implicitly in a descriptive label.

For every perceptual dimension, distinguish:

1. **Observation** — what the reviewer actually hears.
2. **Acceptance** — whether that observation is appropriate for this scene and purpose.

Example:

- ambiguous: `melodrama: PRESENT`
- explicit observation: `melodrama_present: true`
- explicit judgement: `melodrama_appropriate: PASS`

User-facing wording should prefer direct questions whose valence is obvious, for example:

- “Le niveau de dramatisation vous paraît-il approprié à cette scène ?”
- “La voix reste-t-elle naturelle en français ?”
- “Le jeu vous semble-t-il trop appuyé ?”

Rules:

- never assume that `PRESENT`, `ABSENT`, `LIGHT`, `STRONG`, etc. are positive or negative by themselves;
- if a descriptive field is retained for provenance, pair it with an explicit acceptance field;
- every review page must state the PASS condition in plain language before the reviewer submits;
- avoid inverted semantics where selecting a seemingly neutral observation silently causes FAIL;
- when an artistic authority explicitly accepts a perceptual trait, preserve both the raw observation and the acceptance decision.

This rule applies to all future casting, performance, sound-design, H2 and final-master human review surfaces.
