# Odyssée — casting acceptance and integration matrix v1

Authority: #110  
Baseline: `main@ad565381a66a46f823a42ee0a945bbad978fe075`

## Policy

Identity > natural French > performance > number of voices.

Three states are used:

- **HUMAN_ACCEPTED** — perceptually qualified and safe to bind.
- **PROBE_ACCEPTED** — qualified in a promoted scene; safe in that dramatic function.
- **PRODUCTION_CHOICE_H2_WATCH** — usable for a block render, but distinction must be judged in the shared H2 integration session.

A production choice is not mislabeled as human accepted.

## Accepted anchors

| Character | State | Provider / recipe | Locked baseline |
|---|---|---|---|
| Narratrice | HUMAN_ACCEPTED P1/P2 | `fr-FR-DeniseNeural` | rate -5%, pitch -8Hz, volume +1% |
| Ulysse | HUMAN_ACCEPTED P1–P5 | `fr-FR-HenriNeural` | rate -4%, pitch -10Hz, volume +2% |
| Pénélope | HUMAN_ACCEPTED P1 | `fr-FR-VivienneMultilingualNeural` | rate -7%, pitch -4Hz, volume 0% as baseline |
| Télémaque | HUMAN_ACCEPTED P1 | `fr-FR-RemyMultilingualNeural` | rate +5%, pitch +8Hz, volume +2% |
| Athéna | HUMAN_ACCEPTED P1 | `fr-FR-DeniseNeural` | rate -10%, pitch -14Hz, volume -4%; no divine effect |

## Probe-promoted roles / functions

| Character/function | State | Recipe |
|---|---|---|
| Alcinoos | PROBE_ACCEPTED P2 | Remy, rate -8%, pitch -6Hz, volume 0%; restrained secondary authority |
| Euryloque | HUMAN_ACCEPTED P3 collision test | Henri, rate +4%, pitch -14Hz, volume +8%; concrete crew voice |
| Polyphème | HUMAN_ACCEPTED P3 | Remy, rate -10%, pitch -24Hz, volume +3%; mass by cadence, no DSP |
| Anticlée | HUMAN_ACCEPTED P5 H1b | Chatterbox Multilingual V3, exact `P5_UNDERWORLD_ACCEPTED_RECIPE.json` |
| Pénélope — S15 climax | HUMAN_ACCEPTED_LOCAL H1b | preserve P6-B Chatterbox performance conditioned from synthetic Vivienne reference; no global recast implied |
| Sirènes — S09 | BLOCKED_STREAM2 | must arrive as `P4_SIRENS_HUMAN_PASS` |
| Ulysse — S15 emotional lines | BLOCKED_STREAM2 | must arrive as `ULYSSES_EMOTIONAL_HUMAN_PASS`; same identity |

## Secondary production choices

These choices exist to make block production possible. They are deliberately verified in context in H2 rather than through isolated micro-gates.

| Role | Production choice | Direction | H2 watch |
|---|---|---|---|
| Calypso | Vivienne family / warm restrained performance | offer must sound genuinely desirable, never vampish | distinguish from Pénélope across S01→S02 |
| Nausicaa | Eloise fr-FR neutral adult candidate | alert, autonomous, light pace, no child colour | distinguish from Narratrice inside S03 |
| Jeune femme | Vivienne family, brief ensemble function | cautious, no character over-design | no confusion with Nausicaa |
| Éole | Remy family, restrained older authority | practical host, not wizard | no Polyphème residue |
| Circé | Eloise fr-FR, slower controlled authority | threat → comfort with same identity | no “mystical woman” cliché |
| Tirésias | Remy family, low simple cadence | information without oracle theatre | distinct enough from Polyphème by rhythm/context |
| Marin(s) | bounded ensemble reuse | functional crew, never a new lead | do not blur Euryloque |
| Antinoos | Henri-family production performance, dominant and dry | confidence of an occupier, not villain caricature | direct collision with disguised Ulysse in S13/S14 is a priority H2 check |
| Eurymaque | Remy-family production performance, more negotiator than bully | secondary pretender | direct collision with Télémaque is a priority H2 check |
| Eumée | warm restrained adult male production performance | hospitality direct, no noble-retainer voice | distinguish from Ulysse/Télémaque in S12 |
| Euryclée | Eloise-family older restrained performance | warmth; recognition mainly via stop/breath | distinct from Pénélope and Narratrice in S13/S15 |

## Why secondary collisions do not create a pre-render HOLD

The script itself provides strong contextual separation for most secondary roles, and several roles are brief. The expensive mistake would be to open a provider/casting research project before hearing the actual block.

Therefore:
1. render with the bounded production choices;
2. judge collisions inside H2;
3. if a listener cannot reliably identify a material role, recast that role only;
4. do not perturb accepted core identities to solve a secondary collision.

## Ulysse performance continuity

One identity, multiple states:

- S02–S03: weary / socially cautious;
- S04: controlled stranger → storyteller;
- S05: cunning → pride burst;
- S06–S10: command under accumulating loss;
- S11: spent / returned to present;
- S12–S14: disguised restraint, same recognisable identity;
- S15: intimate reaction.

No state authorizes a provider recast.

## Pénélope continuity

- S01: domestic authority and fatigue;
- S13: active listening to the stranger;
- S14: control of the test environment;
- S15: calm trap → recognition release.

The H1b P6-B expressive performance is local evidence for the climax, not permission to exaggerate earlier scenes.
