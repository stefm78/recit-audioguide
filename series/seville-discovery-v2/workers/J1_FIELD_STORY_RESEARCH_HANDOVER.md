# J1 — FIELD STORY RESEARCH — Worker Handover

## Mission

Raise the Seville 3-day field-guide material to the qualitative benchmark established by the live 2026-09-17 walk, without changing route, bookings, logistics, UX, V1 or final audio production.

## Read first

- `series/seville-discovery-v2/FIELD_GUIDE_V2_CONTRACT.md`
- `series/seville-discovery-v2/BASELINE_V1_FALLBACK.md`
- current V1 `series/seville-discovery/series.json`
- current V1 audio and `assets/visit-experience.json` only as source material; do not mutate them.

## Scope

Research the exact physical route in bounded batches. For every meaningful walking interval or stop, identify candidate material that works *on site*:

- one or more visible details the visitor can actually look for;
- human stories and named historical actors when well sourced;
- architectural anomalies, reuse, movement or layering;
- short local legends clearly labelled as legend/tradition;
- before/after contrasts;
- connections to things already encountered on previous days;
- useful walking-time stories for 2–5 minute transfers;
- optional depth candidates that should not burden the primary audio flow.

Prefer memorable, observable and specific material over encyclopedic completeness.

## Required evidence per candidate

Record at minimum:

- stable candidate ID;
- route section / location;
- what the visitor can observe;
- narrative hook;
- concise factual basis;
- legend/tradition status if applicable;
- sources;
- robustness notes: likely visibility, possible closure/scaffolding ambiguity, whether the cue depends on a fragile detail;
- suggested duration class: `20-45s`, `45-90s`, `90-180s`, `DEPTH_ONLY`.

## Priority order

1. Friday morning: NH -> Guadalquivir -> Triana -> Arenal -> NH.
2. Saturday: Pje. de Vila -> Plaza de España -> Santa Cruz -> Archivo.
3. Sunday: Maestranza -> Bellas Artes.
4. Cathedral/Giralda enrichments only after the lighter zones above.
5. Alcázar last: current V1 already has high granularity; add only high-value missing hooks.

## Do not do

- no UX/code changes;
- no audio generation;
- no final showrunner prose;
- no mutation below `series/seville-discovery/**`;
- no route, booking, accommodation or luggage redesign;
- no human-gate requirement.

## Deliverable

Create V2-only research artifacts under `series/seville-discovery-v2/research/`, preferably one bounded file per day or route section plus a source manifest. Return branch/ref, commit SHA, changed paths, coverage achieved and unresolved research uncertainties.

## Stop condition

Stop when additional research no longer changes the best field-story candidates for the currently assigned batch. Do not attempt to exhaust Seville.
