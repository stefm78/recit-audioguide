# STREAM 1 — Odyssée master production roadmap

Authority: #110  
Audited baseline: `main@ad565381a66a46f823a42ee0a945bbad978fe075`  
Narrative freeze authority: `series/odyssee/review/N3_NARRATIVE_FREEZE.md`

## Production objective

Finish a continuous French long-form work in the 75–90 minute editorial envelope without making Voice Lab or provider research the global critical path.

The 15-sequence, 11,788-spoken-word text is frozen. Stream 1 does not rewrite it for taste.

Directing line:

> Il a survécu à tout ce qui pouvait l’empêcher de rentrer ; il lui reste à convaincre sa propre maison qu’il est encore celui qui en est parti.

Climax d’action: S14, les prétendants.  
Climax émotionnel: S15, le lit.

## Exact current state

| Element | State | Production consequence |
|---|---|---|
| Narrative text A–D | FROZEN / PASS | bind renders to exact source blobs; no speculative edits |
| P1 core identity | HUMAN PASS | Narratrice / Ulysse / Pénélope / Télémaque / Athéna anchors usable |
| P2 ownership handoff | HUMAN PASS | S04 → S05 transfer is locked; no jingle |
| Ulysse storyteller watch | CLOSED / PASS in H1 | no global retuning |
| P3 Polyphème / Euryloque | HUMAN PASS | accepted dry/near-dry vocal recipe usable in S05 |
| P4 Sirènes | FAIL / external capability slot | blocks only the Siren performance inside S09 |
| P5 Enfers | HUMAN PASS H1b | use accepted recipe exactly; no reopening without regression |
| P6 staging | HUMAN PASS except Ulysse emotional acting | preserve P6-B staging, Pénélope, pauses and no-music rule |
| Long master | NOT YET ASSEMBLABLE | only because two local vocal packages are missing plus H2/H3 remain |

## Frozen source bindings

| Block | Sequences | Source blob | Spoken words | Editorial window |
|---|---|---|---:|---|
| A | S01–S04 | `c8ec855d8e1096df6ddbbec65f8d0bfc152730f5` | 2,937 | 0–20 min |
| B | S05–S08 | `12a9a582df0dae2949aec7f19f2d526f27943da4` | 3,142 | 20–46 min |
| C | S09–S11 | `4589733f7e7f5302f12511e802cb6a8f0557b1b7` | 1,949 | 46–60 min |
| D | S12–S15 | `a036ae79ba5102af871cb722e0cc5d6ef313236c` | 3,760 | 60–85 min |

Total: 11,788 spoken words.

## Real dependencies on Stream 2

Stream 1 consumes only two provider-agnostic, human-qualified packages.

### 1. P4_SIRENS_HUMAN_PASS

Scope: S09 Siren performance only.

Required evidence:
- attraction PASS, not BORDERLINE;
- French PASS;
- cliché none/light;
- polyphony useful;
- Ulysse/Euryloque identities intact.

Stream 1 does not care whether the provider is local, Azure, Qwen, or another qualified implementation.

No final frozen-text exception for S09 is committed until the passing package proves that a text-architecture change is actually necessary.

### 2. ULYSSES_EMOTIONAL_HUMAN_PASS

Scope: accepted P6-B staging only.

Eligible expressive lines:
- « Non. »
- « Ce lit ne sort pas de cette chambre. »
- « Tu le savais. »
- « Pénélope… »
- « Notre lit. »

The olive-tree explanation stays on the established Ulysse identity without forced emotion unless a concrete regression demonstrates otherwise.

Required evidence:
- Ulysse reaction PASS;
- emotional impact >= 4/5;
- identity continuity PASS;
- French PASS;
- no melodrama.

No recasting, no restaging, no music rescue.

## Work packages

### S1-WP-A — Block A, S01–S04

State: **READY_FOR_STREAM3_BLOCK_RENDER**.

No dependency on P4/P6.

Acceptance focus:
- immediate core identity;
- Pénélope owns the house without becoming cold;
- Ulysse first appears exhausted, not heroic;
- Nausicaa is a young adult, never childlike;
- S04 handoff reproduces P2 perceptually without jingle or score.

### S1-WP-B — Block B, S05–S08

State: **READY_FOR_STREAM3_BLOCK_RENDER**.

No dependency on P4/P6.

Acceptance focus:
- P3 recipe preserved;
- Ulysse's pride after the escape is audible as the causal mistake;
- crew reduction becomes perceptible across S06–S08;
- Circé moves from threat to dangerous comfort without exotic score;
- P5 accepted recipe reproduced exactly.

### S1-WP-C — Block C, S09–S11

State: **PARTIALLY_RENDERABLE**.

Ready now:
- S09 Ulysse/Euryloque/narrative frame;
- S09 sound/staging shell;
- all of S10;
- all of S11.

External slot:
- S09 Siren performance only.

Do not wait on P4 to render/qualify S10–S11 or the non-Siren parts of S09.

### S1-WP-D — Block D, S12–S15

State: **PARTIALLY_RENDERABLE**.

Ready now:
- S12–S14 complete production direction;
- S15 complete staging;
- Pénélope H1b-B performance;
- neutral/explanatory Ulysse lines;
- pauses and no-music rule.

External slot:
- five high-emotion Ulysse lines in S15.

### S1-WP-CAST — Secondary casting collision control

State: **PRODUCTION_CHOICES_READY / H2 WATCH**.

No standalone casting page.

Core anchors and probe-promoted roles are fixed. Secondary roles use bounded audiobook doubling and existing admissible voices/presets. Potential collisions are tested in H2 in context, because a 10-second isolated role audition cannot prove long-form distinction.

A material H2 collision can trigger one targeted recast. No provider exploration is authorized pre-emptively.

### S1-WP-H2 — Block integration

Starts as soon as representative block renders exist; P4/P6 need not be resolved to review independent A/B and nonblocked C/D material.

One GitHub Pages session, not one page per block.

Questions:
- narrative ownership across S04/S05 and S10/S11;
- pacing/fatigue;
- secondary-role collisions;
- sound-density consistency;
- crew-loss continuity;
- Ulysse identity across naufragé / conteur / disguised restraint;
- Pénélope continuity from S01 to S13–S15;
- Argos works without sentimental cue;
- action climax does not steal the emotional climax.

### S1-WP-MASTER — Full assembly and H3

Entry:
1. block renders technically qualified;
2. P4 human-PASS package consumed;
3. Ulysse emotional human-PASS package consumed;
4. no unresolved material H2 defect.

Then:
`assemble → automatic QA → one continuous H3 listening gate → promote master`.

H3 judges the work, not implementation details.

## Steve challenge

Reject:
- technically neat transitions that call attention to themselves;
- decorative sea/music that reduces intimacy;
- a spectacular S14 that emotionally exhausts the listener before S15;
- a secondary casting scheme that makes the listener identify providers instead of characters.

Listener continuity beats implementation symmetry.

## Linus challenge

Reject:
- a global HOLD because two clips are unresolved;
- new engine features for scene-local problems;
- new human gates for machine-verifiable facts;
- exhaustive asset acquisition before the block proves it needs the asset;
- speculative script revisions.

Prepare independent work now; replace only the two qualified slots later.

## Stop rules

- P5 is closed unless a concrete reproduction regression appears.
- P4 remains Stream 2 owned.
- P6 restaging is closed; only Ulysse emotional performance remains open.
- The frozen script changes only for downstream oral/comprehension/factual/production defects with evidence.
- No generic Audio Engine architecture modification from Stream 1.
