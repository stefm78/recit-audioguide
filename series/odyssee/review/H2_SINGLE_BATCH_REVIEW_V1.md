# Odyssée — H2 final partagé

Authority: #110  
Downstream: #112  
Machine-readable contract: `series/odyssee/review/H2_SINGLE_BATCH_REVIEW_V1.json`  
Review surface: `web/reviews/odyssee-h2.html`

Status: **H2_SINGLE_BATCH_REVIEW_READY_PENDING_AUDIO**

## Why the historical H2 scope is superseded

The historical H2 plan was designed while P4 and P6 were unresolved capability risks. It therefore favored representative scenes and conditional additions.

That is no longer the right product question.

P4 and P6 are now artistically closed:
- P4 = `P4_SIRENS_HUMAN_PASS`;
- P6 = `ULYSSES_EMOTIONAL_HUMAN_PASS`;
- P5 is closed;
- MARIN / Block B is closed machine-side;
- Stream 2 is out of the critical path.

H2 must therefore review the **real integrated work**, not re-certify capabilities.

H2 is now a long-form structured integration review. H3 remains different: H3 is the single uninterrupted final-master listen.

## Hard entry gate

Do not dispatch H2 before Stream 3 explicitly confirms:

`A+B+C+D MACHINE_QUALIFIED`

The immutable review Release must contain, in one Release:
- `block-A.mp3`, `block-B.mp3`, `block-C.mp3`, `block-D.mp3`;
- matching block QA reports;
- `scene-S09.mp3`, `scene-S13.mp3`, `scene-S14.mp3`, `scene-S15.mp3`;
- matching scene QA reports;
- `review-index.json`.

A partial review Release is not H2.

The H2 page is fail-closed and remains locked when any required asset is missing.

## One batch only

There is exactly one H2 batch.

No:
- H2a / H2b;
- Siren micro-review;
- MARIN micro-review;
- P6 micro-review;
- transition micro-gate;
- separate loudness human gate.

Machine failures are fixed before H2. Capability probes are already closed.

## Mandatory listening order

### 1. Block A — full continuous listen

Purpose:
- long-form reference;
- pacing / comprehension baseline;
- fatigue baseline;
- narrator ↔ character ownership;
- reference level and production continuity.

The reviewer should not judge whether the duration matches a spreadsheet. The question is whether first-listen comprehension and attention remain strong.

### 2. Block B — full continuous listen

Purpose:
- MARIN in real dialogue with Euryloque / Ulysse;
- P5 / S08 in the complete block;
- dense loss sequences;
- intentional subtraction and silence;
- level continuity from A.

MARIN is not a casting question. H2 only asks whether the frozen production choice works in context.

P5 is not reopened. H2 only asks whether the accepted recipe integrates correctly into the block.

### 3. S09 — full real scene

Purpose:
- P4 in the frozen scene rather than the compact probe;
- two Siren lineages;
- subtle left/right placement;
- attraction through attention / recognition / knowledge;
- French intelligibility;
- Ulysse identity continuity.

Do not ask whether VoxCPM2 is a good capability. That gate is closed.

### 4. B → C boundary

Listen to approximately:
- final 45 seconds of Block B;
- first 45 seconds of Block C.

Judge:
- narrative continuity;
- acoustic-space transition;
- level continuity;
- whether S09 enters as a dangerous change of attention rather than a production gimmick.

### 5. C → D boundary

Listen to approximately:
- final 45 seconds of Block C;
- first 45 seconds of Block D.

Judge:
- return-to-Ithaca continuity;
- narrative ownership;
- energy reset before the recognition / climax sequence;
- level continuity.

### 6. S13 — full scene

Judge:
- recognitions;
- secondary-cast readability;
- Argos restraint;
- Pénélope continuity;
- whether the scene prepares the climax without spending it.

### 7. S14 — full scene

Judge:
- action clarity;
- restraint of violence;
- absence of decorative impact catalogue;
- sound-density drop after action;
- emotional headroom remaining for S15.

### 8. S15 — full real Production scene

This is mandatory and replaces any temptation to judge P6 from a probe.

H2 hears:
- the exact 12 frozen Ulysse emotional lines in Production;
- the accepted Pénélope materialization;
- the real pauses and context;
- the complete bed-test scene;
- capture / conversion / level / splice hygiene.

The raw human recording is not a review artifact.

The capability is not reopened.

Judge whether the **finished scene** works.

### 9. Global A/B/C/D comparison

Short comparative listening across the four blocks.

Judge:
- global dynamics;
- relative levels;
- identity stability;
- fatigue after extended listening;
- whether production machinery becomes audible.

## Human review semantics

Every criterion has two separate fields.

### Observation

Describe what is actually heard.

Examples:
- “la Sirène gauche paraît plus proche”;
- “un clic est audible avant la réplique”;
- “la dramatisation est très présente”;
- “le passage S06 paraît très dense”.

Observation is descriptive only.

### Artistic verdict

Choose `PASS` or `FAIL` against the explicit condition shown on the page.

A descriptive term never implies artistic value.

Bad:
`melodrama = PRESENT` → implicit failure.

Correct:
- observation: `melodrama_present = true`;
- artistic verdict: `melodrama_appropriate = PASS`.

This separation is mandatory for all H2 dimensions.

## H2 criteria

H2 covers all of the following:

1. pacing and first-listen comprehension;
2. listening fatigue;
3. identity coherence;
4. MARIN in context;
5. P5 / S08 integration;
6. P4 / S09 real-scene integration;
7. B→C and C→D transitions;
8. S13/S14 climax preparation;
9. S15 emotional climax;
10. global dynamics;
11. sound density and intentional silence;
12. inter-block level continuity;
13. absence of material audible technical defects.

The exact PASS condition for every criterion is encoded in the machine-readable contract and displayed before the reviewer enters a verdict.

## Decision rule

Only two final outcomes exist:

- `PASS_H2_SINGLE_BATCH`
- `FAIL_H2_TARGETED_CORRECTION`

PASS requires every mandatory criterion to PASS.

There is:
- no score average;
- no compensating “4/5 overall”;
- no partial H2 promotion.

On FAIL:
- record the perceptual observation;
- identify the smallest causal production unit;
- fix only that unit;
- re-listen only the changed causal scope plus any affected transition.

H2 does not automatically reopen:
- casting;
- asset search;
- script;
- provider research.

## Product stop rules

Do not:
- add sound merely to make the work feel “finished”;
- start a new asset search without a concrete audible defect;
- decorate intentional silence;
- global-slow the work from WPM arithmetic;
- re-run casting because an integration defect exists;
- dispatch H2 before `A+B+C+D MACHINE_QUALIFIED`.

## Ready state

All review logic, scope, criteria and fail-closed release binding can be completed before final audio exists.

Once Stream 3 confirms the hard gate and publishes the immutable review Release, the only action required is to open:

`/reviews/odyssee-h2.html?tag=<immutable-review-release-tag>`

No additional artistic preparation should be necessary.

**Target state: `H2_SINGLE_BATCH_REVIEW_READY_PENDING_AUDIO`.**
