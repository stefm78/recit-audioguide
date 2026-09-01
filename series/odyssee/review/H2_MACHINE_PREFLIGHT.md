# Odyssée — H2 machine preflight

Authority: #110  
Production evidence: run `33497013375`  
Product source used by run: `31030ac45c5343b23a2e7c858f49990e888c9a1a`  
Generic runtime used by run: `stefm78/audio-engine@52c933b6371103b977a2ccbcade291700bd0eb73`  
Current product main when this preflight is recorded: `5de36966a3fb7ceb38c2108609776350c221894f`

Status: **H2_PREP_ACTIVE — MACHINE PREFLIGHT PASS WITH PACING WATCH**

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

The Actions artifact is evidence, not durable human-review authority because it expires. H2 must bind a durable release/Pages-consumable asset before human review.

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

When durable assets exist, one page should expose:

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

- Block A is ready;
- the highest-value independent scenes are rendered;
- P4 is actively rendering in Stream 2;
- P6 current failure is pre-synthesis infrastructure, not artistic evidence;
- generic multi-provider routing needed by P5 is already merged in Audio Engine;
- a short wait for durable assets and near-term integrations can materially increase the value of one listening session.

This is not a global production hold. Stream 1 continues machine preparation while downstream renders progress.

## Stop rules

- no speculative narrative edits;
- no global slowdown based only on WPM;
- no new casting research from Stream 1;
- no duplicate review issue;
- no human gate until audio references are immutable and browser-consumable;
- if H2 identifies a defect, fix the smallest causal unit and re-listen only what changed.
