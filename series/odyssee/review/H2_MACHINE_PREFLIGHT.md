## Current frozen P7 conclusion — Ulysse escalated, Télémaque separated

Stream 1 final P7 Ulysse conclusion:

`P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER`

The Edge artistic budget is exhausted.

Hard rules:
- no Round 3 Edge;
- no Ulysse recast;
- no frozen-text change;
- preserve Henri/Ulysse identity target.

New Ulysse lane:
- issue #179 — Stream 2 performance-provider escalation preserving Henri/Ulysse identity.

Separate production defect:
- issue #178 — Télémaque French language-integrity defect on RemyMultilingual / Edge.

Separation rule:
- #178 does **not** block or qualify the P7 Ulysse conclusion;
- #178 does block S12 final production, Block D machine qualification and H2 until French-clean Télémaque exists;
- #179 owns the Ulysse performance path from this point forward.

Therefore H2 remains suspended for two independent reasons:
1. Ulysse performance-provider path #179 not yet accepted/materialized;
2. Télémaque French integrity #178 not yet resolved.

Do not use Télémaque to reopen Edge or defer the P7 Ulysse escalation conclusion.


# Odyssée — H2 machine preflight

Authority: #110  
Production evidence: run `33497013375`  
Product source used by run: `31030ac45c5343b23a2e7c858f49990e888c9a1a`  
Generic runtime used by run: `stefm78/audio-engine@52c933b6371103b977a2ccbcade291700bd0eb73`  
Current product main when this preflight is recorded: `5de36966a3fb7ceb38c2108609776350c221894f`

Status: **H2_SUSPENDED_ULYSSE_PROVIDER_AND_TELEMAQUE_INTEGRITY**

## Frozen Round 2 human result — Edge artistic budget exhausted

Authority:
`series/odyssee/review/P7_ROUND2_HUMAN_REVIEW_V1.json`

Human result:
- context integrity FAIL because Télémaque still has audible non-French passages;
- Ulysse/Henri identity PASS in all four states;
- Ulysse French natural PASS in all four states;
- storyteller / loss / father / authority all remain artistically FAIL because C2 is **not materially less mechanical/cold than B1**;
- dramatic-state fit, living rhythm and restraint/no-caricature are otherwise acceptable.

The review page returned:
`P7_ROUND2_PROBE_INTEGRITY_FAIL`

Its field:
`edge_budget_exhausted:false`

is a **non-authoritative page-logic artifact** caused by deriving that field from the final decision code. It does not reopen Edge.

Stream 1 authoritative arbitration:
- Round 2 is the final artistic Edge attempt;
- Edge artistic budget = **EXHAUSTED**;
- no Round 3 Edge is authorized;
- no Ulysse parameter may be changed during the technical repair;
- the only admissible next action is minimum Télémaque/context language-integrity repair;
- technical repair does not replenish the artistic budget;
- once technical integrity is restored, any remaining/confirmed artistic FAIL authorizes `P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER`.

H2 remains suspended.

## Current P7 suspension — Round 2 final Henri/Edge budget

Round 1 human result:
- Henri/Ulysse identity PASS;
- Ulysse French PASS;
- all four directed B states FAIL on less-mechanical/cold, dramatic-state fit and living rhythm;
- no caricature finding;
- father probe also exposed a separate technical context defect: Télémaque has audible English passages.

Round 1 decision:
`P7_EDGE_BOUNDED_RETUNE_REQUIRED`

Round 2 is deliberately method-distinct within the same identity:
- same `fr-FR-HenriNeural`;
- no recasting;
- no frozen-text change;
- no provider change;
- four C candidates only;
- per-segment rate/pitch/volume/pause micro-prosody instead of one state-wide preset;
- explicit `language_locale=fr-FR` on every Edge segment to remove the father probe context-language defect without changing voice/text.

Authority:
- `series/odyssee/review/P7_ROUND1_HUMAN_REVIEW_V1.json`;
- `series/odyssee/review/P7_ULYSSE_PERFORMANCE_CONTINUITY_ROUND2_V1.json`;
- `web/reviews/odyssee-p7-round2.html`.

This is the **final Edge round**.

Decision after technically valid Round 2:
- PASS -> `P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS`;
- artistic FAIL -> `P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER`;
- no Round 3 Edge.

A remaining non-French context defect is `P7_ROUND2_PROBE_INTEGRITY_FAIL` and authorizes technical locale/transport repair only; it does not consume an artistic retry or imply Ulysse failure.

H2 resume requires:
`P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS + A+B+C+D MACHINE_QUALIFIED`.

## Current H2 authority — final shared batch

The historical H2 scope below is retained as production history but is **superseded** for human review design.

Current artistic/product facts:
- P4 = `P4_SIRENS_HUMAN_PASS`; H2 reviews the real complete S09 integration, not the capability;
- P5 is closed; H2 reviews P5/S08 only as part of Block B integration;
- MARIN / Block B is machine-side closed; H2 reviews MARIN only in real context;
- P6 = `ULYSSES_EMOTIONAL_HUMAN_PASS`; the only remaining pre-H2 human work is clean Production capture of the exact 12 frozen S15 Ulysse lines, owned by Stream 3;
- Stream 2 has exited the critical path;
- no casting research is authorized.

Final H2 authority:
- `series/odyssee/review/H2_SINGLE_BATCH_REVIEW_V1.md`;
- `series/odyssee/review/H2_SINGLE_BATCH_REVIEW_V1.json`;
- `web/reviews/odyssee-h2.html`.

Hard entry gate:
`A+B+C+D MACHINE_QUALIFIED`

The review surface is fail-closed against one immutable review Release and requires:
- Block A/B/C/D audio + QA;
- complete S09/S13/S14/S15 audio + QA;
- `review-index.json`.

Final mandatory scope:
1. Block A continuous;
2. Block B continuous;
3. S09 complete;
4. B→C boundary;
5. C→D boundary;
6. S13 complete;
7. S14 complete;
8. S15 complete;
9. global A/B/C/D comparison.

Decision semantics:
- observation is descriptive;
- artistic acceptance is a separate PASS / FAIL;
- `PRESENT`, `ABSENT`, `LIGHT`, `STRONG` never carry implicit valence;
- final outcomes are only `PASS_H2_SINGLE_BATCH` or `FAIL_H2_TARGETED_CORRECTION`.

This preparation is complete before final audio exists.

Target state:
`H2_SINGLE_BATCH_REVIEW_READY_PENDING_AUDIO`.

## Historical delta — post P5 product integration (superseded)

As of product main `b55834cc2f6ed75dc1f243048aa39282bd89f9ed`:

- P5/S08 product binding is promoted and validated;
- S08 is now `sound-integrated-p5-v1` at the Program/product-contract level;
- its first full Production render still fails on a runtime `ffprobe` defect after provider/model/reference hydration succeeds;
- this is **technical only** and does not reopen the HUMAN_PASS P5 recipe;
- Block B is therefore not yet an H2 audio candidate.

A second materialization gap remains:

- the current Production voice pack still maps `odyssee-marin-h2` to the exact Euryloque Henri preset;
- the Stream 1 correction to `fr-FR-AlainNeural` has **not yet been consumed**;
- S05/S06/S07/S10 remain ineligible for human H2 until the corrected MARIN renders exist.

Exact sound-direction locators for S02/S05/S06/S08/S14 are now authoritative in:
`series/odyssee/production/H2_SOUND_DIRECTION_BINDINGS_V1.json`.


## Current authoritative delta — 2026-09-02

As of product main `dae91ec3870b77a6fb49598ff47f1bc33d3fbf28`:

- P5/S08 is fully industrialized and machine-ready; Production run `33525198119` is automatic-QA PASS. The earlier `ffprobe` defect is closed and must not reopen P5 artistically.
- bounded sound acquisition is complete. The three optional assets produced no automatic selection at the authorized threshold; Stream 1 therefore accepts the authored fallbacks: deliberate silence / omit-and-warn / ensemble subtraction. No manual best-of-N, threshold reduction or fourth asset is authorized.
- P4 Sirens is HUMAN_PASS and product-bound exactly through `P4_FROZEN_S09_BINDING_V1.json`; S09 now waits only on Stream 3 materialization, not on Stream 2.
- MARIN V2 / Alain is retired because the voice is absent from the current Edge catalog. Stream 1 V3 is `fr-FR-RemyMultilingualNeural`, rate `+3%`, pitch `-4Hz`, volume `+2%`; deterministic audit found zero direct MARIN ↔ Remy-family adjacent turns across S05/S06/S07/S10. Those four scenes await narrow Stream 3 rerender only.
- P6/Confucius4 produced one MACHINE_PASS candidate in run `33598325723`, candidate SHA-256 `55702f253cbfc9c758d02d7f9952a94dfb68d2877f402fc0a5e6215bec0b2b9d`. It is not product-consumable until Stream 2 publishes `ULYSSES_EMOTIONAL_HUMAN_PASS`.
- the exact frozen S15 binding has been revalidated against current Program blob `2d07fd4bc16d77286012e641948bd1b5b3e2100b`: 37/37 guards PASS, zero mismatches.

H2 remains a single batched human session. Do not dispatch it yet: the value of one review will materially increase once corrected MARIN/Block B and P4/Block C renders are available, while P6 can remain independent if its human verdict is still pending.

This file is not a human verdict. It narrows the future H2 listening session to questions that machine QA cannot answer.

## Evidence available

First industrial production run produced:

- S01–S07: rendered;
- S10–S14: rendered;
- S08: held on generic local-provider integration for already-human-PASS P5;
- S09: held on `P4_SIRENS_HUMAN_PASS`;
- S15: held on local-provider integration plus `ULYSSES_EMOTIONAL_HUMAN_PASS`;
- Block A / S01–S04: assembled;
- Block A assembly QA: PASS;
- all 12 rendered scene QA reports: PASS with `failed_checks=[]`.

Block A immutable Actions artifact from this run:

- artifact: `odyssee-production-v1-block-A`;
- artifact id: `9796283623`;
- artifact ZIP SHA-256: `1e0991364fa1d257d0cc097ab80434594209d419ccd2ed95f3b3bd79fecba958`;
- measured assembly duration: **1017.6 s / 16:57.6**.

The Actions artifact is evidence, not durable human-review authority because it expires. In addition, this Block A is a speech-only `scene-foundation-v1` assembly. H2 requires an integrated sound-direction render and a durable release/Pages-consumable asset.

## Render maturity correction — voice foundation is not H2 integration

Audit of the materialized scene Programs on current main shows:

- S01–S15 are marked `stage: scene-foundation-v1`;
- current rendered Programs contain speech segments only;
- `soundscape`, `ambience`, `music` and transition execution are absent from the current scene Programs;
- the first industrial Block A therefore proves **voice rendering, timing, fan-in and technical QA**, not final artistic integration.

Classification:

`FIRST_INDUSTRIAL_RUN = VOICE_FOUNDATION_EVIDENCE`

It is valid evidence for:
- pacing risk;
- vocal identity;
- casting collisions;
- narrative ownership carried by voices;
- pipeline reproducibility.

It is **not yet an H2 human candidate** for:
- sound-density consistency;
- scene-space transitions;
- event punctuation;
- S14 action-vs-S15 headroom;
- the full listener experience.

### H2 entry contract

There remains exactly **one H2**, not H2a/H2b.

Before its human page is published, Stream 3 must materialize the product-owned sound direction into the review candidates. “Materialize” does not mean adding sound everywhere: an explicit dry/silence choice is valid when that is the artistic direction.

Minimum contract:

1. preserve frozen speech and accepted voice identities;
2. implement only narratively justified sound/space decisions from `production/blocks/BLOCK_A.md` … `BLOCK_D.md`;
3. preserve intentional silence and avoid permanent sea/music/crowd beds;
4. include scene/block transitions where they are part of the listening judgment;
5. bind every non-generated audio asset to provenance/license/integrity evidence;
6. machine-QA the resulting integrated scenes/blocks;
7. publish immutable browser-consumable audio for H2.

High-value required punctuations before H2:
- S02: storm/breakage as a bounded event, not a sea bed;
- S05: confinement/stone only as useful punctuation; no monster DSP;
- S06: bag opening wind event + compressed destruction; fleet reduction must become perceptible;
- S08: exact accepted P5 dark-air recipe, no extra layer;
- S14: bow/string as privileged punctuation + short legible violence + sharp density drop toward S15.

Other supportive layers may be omitted if silence/voice better satisfies the block direction.

The existing speech-only renders should be reused wherever the engine can compose sound around immutable speech. They must not be rerendered merely to add ambience unless the generic runtime requires it.

## Machine pacing table

| Scene | Frozen spoken words | Render duration | Approx. spoken density |
|---|---:|---:|---:|
| S01 | 1,134 | 6:34 | 172.7 wpm |
| S02 | 848 | 4:40 | 181.6 wpm |
| S03 | 536 | 3:12 | 167.2 wpm |
| S04 | 419 | 2:31 | 166.4 wpm |
| S05 | 808 | 5:02 | 160.5 wpm |
| S06 | 877 | 4:43 | 185.8 wpm |
| S07 | 836 | 4:52 | 171.7 wpm |
| S10 | 797 | 4:19 | 184.6 wpm |
| S11 | 608 | 3:52 | 157.3 wpm |
| S12 | 1,202 | 6:54 | 174.1 wpm |
| S13 | 1,030 | 6:05 | 169.1 wpm |
| S14 | 606 | 3:44 | 162.7 wpm |

Rendered subset:

- spoken words: **9,701**;
- duration: **56.49 min**;
- aggregate density: **171.7 wpm**.

If the three held scenes behaved at the same aggregate density, the frozen 11,788-word work would land around **68.6 min**.

This is a **risk signal, not a failure**:

- held P5/P4/P6 material may be slower;
- scene pauses and dramatic density matter more than arithmetic WPM;
- editorial windows in the block plan are approximate;
- accepted voice identities/rates must not be globally retuned from a spreadsheet.

However, the ~75-minute product objective and the accessibility target make pacing a first-class H2 question.

## Technical consistency

Integrated loudness measured on rendered scenes is tightly grouped:

- minimum: about -17.14 LUFS;
- maximum: about -16.68 LUFS;
- spread: about 0.46 LU.

No loudness-normalization correction is requested by Stream 1.

Machine QA found no abnormal assembly silence in Block A and no technical scene failures. No artistic conclusion is inferred from those checks.

## Deterministic casting defect found and corrected before H2

A Program/voice-pack adjacency audit found that `MARIN` and Euryloque used the exact same Henri voice and exact same synthesis parameters.

Direct alternating turns with identical voice identity:

- S05: 5;
- S06: 32;
- S07: 17;
- S10: 9;
- total: **63**.

This is not left for the human reviewer because the causal defect is already known.

Stream 1 correction:

- Euryloque remains unchanged and human-accepted;
- MARIN V2 / Alain was attempted but is unavailable in current Edge; MARIN V3 is `fr-FR-RemyMultilingualNeural`, rate +3%, pitch -4Hz, volume +2%;
- only S05/S06/S07/S10 are rerendered;
- those four first-run audios are no longer H2 review candidates;
- the first-run metrics above remain valid as pipeline and pacing evidence, but pacing for the corrected renders must be remeasured.

No other H2-watch role is pre-emptively recast.

## H2 hypotheses — only these require ears

### H2-PACE-1 — long-form breathing

Listen to Block A continuously.

Question:

> Does 16:58 feel alive and clear, or compressed enough that an accessible listener starts losing information?

Do not ask whether it "should be 20 minutes". Duration is evidence, not the artistic criterion.

Priority watch:

- S02, because its measured density is ~181.6 wpm;
- whether S01→S02 gives enough cognitive reset;
- whether S03/S04 recover enough air before the narrative handoff.

### H2-PACE-2 — dense exposition / action

Priority scenes:

- S06 — ~185.8 wpm;
- S10 — ~184.6 wpm.

Question:

> Can a listener follow cause, loss and geography on first hearing without mentally chasing the narration?

A FAIL authorizes a local pacing correction only. It does not authorize global voice-rate retuning.

### H2-OWNERSHIP — present → Ulysse → present

Must eventually be heard across:

- S04→S05;
- S10→S11.

Required:

- Ulysse clearly owns the central remembered journey after S04;
- Narratrice clearly retakes the present in S11;
- no jingle or artificial chapter marker is needed to explain ownership.

### H2-CAST-COLLISION — secondary roles

Priority real-scene checks:

- S13/S14: Antinoos vs disguised Ulysse;
- S13/S14: Eurymaque vs Télémaque;
- S13: Euryclée vs Pénélope/Narratrice;
- S02: Calypso vs established Pénélope-family timbre continuity risk;
- S12: Eumée vs male anchors.

Only a **material identification collision** justifies targeted recasting. No standalone micro-casting loop.

### H2-ULYSSE-CONTINUITY

Compare:

- S05 storyteller / pride;
- S10 command under loss;
- S11 spent return to present;
- S12–S14 disguised restraint.

Required:

> one recognisable Ulysse identity, different dramatic states.

No provider recast is authorized.

### H2-CLIMAX-HEADROOM

S14 must be exciting without emotionally exhausting the listener before S15.

Final judgment remains impossible until S15 exists.

Current H2 can still detect an obvious S14 excess:

- victory-anthem effect;
- excessive loudness/density;
- lingering action energy that would leave no room for the dry bed scene.

## Recommended single H2 review surface

Do **not** launch human review from the expiring Actions artifacts.

When sound-integrated durable assets exist, one page should expose:

1. Block A continuous assembly — mandatory full listen;
2. S05 — P3 integration + Ulysse/Euryloque/Polyphème;
3. S11 — ownership return to Narratrice;
4. S13 — densest casting collision / recognitions;
5. S14 — action climax / S15 headroom;
6. later, only if available before H2 publication:
   - complete Block B once P5 is industrially reproduced;
   - S09 only after `P4_SIRENS_HUMAN_PASS`;
   - S15 only after `ULYSSES_EMOTIONAL_HUMAN_PASS`.

The page should ask one compact set of transverse questions, not one verdict per scene.

## Human timing decision

**Do not request human H2 yet.**

Reason:

- Block A voice foundation is ready, but its product sound direction is not yet materialized;
- the highest-value independent scenes are machine-ready; S05/S06/S07/S10 require the narrow MARIN V3 rerender and S09 requires P4 materialization before the shared H2 batch is worth dispatching;
- P4 is HUMAN_PASS and exact S09 binding is complete; Stream 3 materialization is pending;
- P6 Confucius4 is MACHINE_PASS and awaits the only remaining Stream 2 human verdict;
- generic multi-provider routing needed by P5 is already merged in Audio Engine;
- a short wait for durable assets and near-term integrations can materially increase the value of one listening session.

This is not a global production hold. Stream 1 continues machine preparation while downstream renders progress.

## Stop rules

- no speculative narrative edits;
- no global slowdown based only on WPM;
- no new casting research from Stream 1;
- no duplicate review issue;
- no human gate until audio references are sound-integrated, immutable and browser-consumable;
- if H2 identifies a defect, fix the smallest causal unit and re-listen only what changed.
