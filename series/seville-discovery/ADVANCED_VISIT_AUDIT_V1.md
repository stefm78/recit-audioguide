# Séville — Advanced Visit Audit V1

Date: 2026-09-10
Baseline: main `79c7d6e65f90a5c39646113b35cbfd631cfd9dd4`
Mission: improve the on-site discovery experience without reopening the qualified 3-day route or bookings.

## Finding

The existing series already had a strong intellectual spine and useful `launch` / `look` metadata, but the Web surface remained episode-list centric and the core scripts were often linear explanatory blocks. The largest material gap was not route planning: it was field attention management — what to look at first, when to stop listening, when to compare, and how to expose optional depth without cognitive overload.

## Episode matrix

| Episode | Disposition | Reason |
| --- | --- | --- |
| ep06 Guadalquivir / Triana | KEEP + FIELD LAYER | Strong prologue; field cues add observation and silence without rewriting audio. |
| ep07 Triana / Arenal | KEEP + FIELD LAYER | Existing narrative already treats return as meaningful; add compare/move cues. |
| ep04 Giralda / Cathédrale | IMPROVE | High-value monument; previous script was too lecture-like and still said “two days”. Rewritten field-first. |
| ep02 Alcázar | IMPROVE | Intellectual heart of trip; rewritten around look → reveal → silence → compare. |
| ep00 approach to Plaza de España | KEEP + FIELD LAYER | Movement already useful; field program makes the gradual opening explicit. |
| ep05 Plaza de España | KEEP + FIELD LAYER | Main interpretation remains sound; cues enforce whole-before-detail observation. |
| ep01 Santa Cruz | IMPROVE | Walking episode benefits materially from embodied observation and deliberate silence; rewritten field-first. |
| ep03 Archivo de Indias | KEEP + FIELD LAYER | Core thesis is good; field layer reduces risk of abstract lecture while walking. |
| g02 Casa de Pilatos | KEEP + FIELD LAYER | Existing optional episode remains useful; comparison with Alcázar becomes explicit in field layer. |
| g13 Bellas Artes | KEEP + FIELD LAYER | Existing calm epilogue remains appropriate; field layer adds one-work / one-minute silence discipline. |

## Grammar adopted

`ARRIVAL`, `LOOK`, `STORY`, `REVEAL`, `MOVE`, `SILENCE`, `COMPARE`, `HUMAN_STORY`, `OPTIONAL_DEPTH`, `EXIT`.

The grammar is additive and optional. It is encoded in `assets/visit-experience.json` and documented in `docs/VISIT_EXPERIENCE_V1.md`.

## Web change

For visit series carrying the optional asset, `web/next-step.js` now adds:

- a **Maintenant** card selecting the first not-completed episode;
- the reason the current step matters;
- “Regardez d’abord” guidance;
- approximate field duration;
- immediate listen / route / step actions;
- expandable on-site field cues;
- existing next-step routing remains intact.

Series without the asset are unchanged.

## Historical / source audit

The rewritten Cathédrale / Giralda script is grounded in official Catedral de Sevilla material, notably the Giralda structure and Patio de los Naranjos. The Alcázar rewrite retains the official Real Alcázar sources already attached to the episode. The Santa Cruz rewrite keeps the existing official tourism sources and avoids introducing new precise claims beyond the already-established interpretation.

Interpretive language is deliberately separated from observable prompts. Legends are not promoted to facts.

## Sound direction decision

No new decorative sound bed was added in this package. The material improvement comes from attention transfer and intentional silence; adding speculative historical ambience would increase production complexity without proven field value. Existing Sound Director capabilities remain available for a later human listening review if the new renders demonstrate a specific need.

## Qualification question

Is the candidate materially better than reading a fact sheet while following Google Maps?

Candidate answer to verify after CI / render / page publication: **YES, if the new field companion is usable on mobile and the three rewritten audio episodes render cleanly.**
