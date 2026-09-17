# J2 — FIELD SHOWRUNNER — Worker Handover

## Mission

Convert bounded J1 research into the V2 field-scene program. Preserve the 3-day route and operational constraints; change the lived narrative granularity.

## Preconditions

Start only from a bounded J1 research batch that coordination has accepted as sufficient for that route section. Do not wait for all three days before beginning.

Read:

- `FIELD_GUIDE_V2_CONTRACT.md`
- `BASELINE_V1_FALLBACK.md`
- relevant J1 research artifacts
- current V1 episode/audio material for continuity only.

## Output model

The lived unit is a scene, not a long episode. Compose only what the place and walking interval justify.

Preferred grammar:

`PROMISE -> MOVE -> LOOK/SEARCH -> REVEAL -> HUMAN_STORY/CONTEXT -> CONNECT -> SILENCE/MOVE -> NEXT_PROMISE`

A scene may omit elements. Avoid formulaic repetition.

## Required scene fields

At minimum:

- stable scene ID;
- day / route section / ordering;
- trigger or launch condition stated without requiring precise geofencing;
- scene type;
- spoken text;
- expected duration class;
- observable cue where relevant;
- fallback behavior for `Je ne trouve pas` where relevant;
- next-scene relation;
- source/candidate references from J1;
- optional-depth links where appropriate.

## Editorial rules

- audio-first, oral French;
- observation before explanation when useful;
- concrete and human before encyclopedic;
- distinguish attested history, hypothesis and legend;
- reuse walking time when there is worthwhile material;
- preserve silence where the place is stronger than narration;
- connect later scenes to things already observed earlier in the trip;
- do not overload names, dates or abstractions;
- do not lengthen material merely to increase audio minutes.

## Boundaries

No UX/shared-code changes. No production audio generation. No V1 mutation. No route/booking/logistics changes. No human audio gate.

## Deliverable

Write V2-only scene/program artifacts under `series/seville-discovery-v2/scenes/` or an equivalent V2 namespace agreed with J3. Return branch/ref, commit SHA, changed paths, scene count, route coverage, source traceability and unresolved field assumptions.
