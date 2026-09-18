# Séville Field Guide V2 — Coordination Head

Status: ACTIVE_EXECUTION

Integration branch: `seville-field-guide-v2`
Frozen V1 path: `series/seville-discovery/**`
V2 path: `series/seville-discovery-v2/**`

## Kernel-native coordination

The coordinating discussion is the durable DRIVE/HEAD authority for this workstream, but it does not replace the ACTIVE kernel authority.

Use the ACTIVE primitives causally:

- `/refresh` — reconstruct current authoritative kernel state plus the smallest durable project view needed to coordinate workers; always revalidate integration HEAD before integration mutation.
- `/solve` — arbitrate worker overlap, integration order, cross-stream conflicts, candidate selection and any material change of plan.
- `/build` — perform bounded coordination mutations such as branch preparation, handover updates, integration/cherry-pick/merge and coordination-state materialization after freshness checks.
- `/audit` — independently verify integrated candidate invariants after material integration steps.
- `/research` — only when coordination itself lacks external/current evidence required for an arbitration; do not duplicate worker research.
- `/learn` — only for a durable, reusable lesson that generalizes beyond this Seville V2 execution.

Default coordination cycle when mutation is required:

`/refresh -> /solve (if a material decision exists) -> /build -> /audit`

## Integrated evidence

### J1 — Field Story Research

COMPLETE / INTEGRATED for Friday, Saturday and Sunday.

- Friday accepted worker SHA: `0d131065708cedc6853dc1c844cd0cfd50473441`.
- Saturday accepted worker SHA: `ab368ca8225e4e87fd29976637608a10adcf5812`.
- Sunday accepted worker SHA: `4ca3af65748cd240025ae9e556850d48a4ace05a`.
- Sunday remains Maestranza -> checkout / Lockers Agua -> Museo de Bellas Artes -> protected airport departure; Casa de Pilatos is fallback-only.

### J2 — Field Narrative Showrunner

COMPLETE / INTEGRATED for Friday, Saturday and Sunday.

- Friday accepted worker SHA: `4f7d7f3dace0890274acc5470bf76e5ac6f9d3d3`; 8 primary scenes + 3 optional depth.
- Saturday accepted worker SHA: `9fa00643e7ac74f324dd2947ba9b09d785e5e842`; 8 primary scenes + 5 optional depth.
- Sunday accepted worker SHA: `19c70040429d1dffc106f94ffd7dde3654477232`; 9 primary scenes + 4 optional depth.
- All optional-depth audio remains deferred; primary scene total = 25.

### J3 — Audio-first UX

COMPLETE / INTEGRATED from worker SHA `ae64ce952100d5dacf676de968451723b830b4bb`.

- `AUDIO_FIRST_UX_CAPABILITY.json` accepted.
- shared `web/next-step.js` remains capability-gated and preserves legacy `firstPendingIndex` behavior.
- V1 fallback contract is `../seville-discovery/`.

### J4 — Audio Production

COMPLETE / INTEGRATED for all 25 primary scenes.

- Friday final worker SHA `06ce0580fade766f8a4bfe0dd0e8721899b0d3b6`; run `35260567914`; artifact `10514517681`; 8/8 rendered and decoded; French lock PASS.
- Saturday final worker SHA `8fd82f816430a6fd77d0209a808d90e1af9ee0ad`; run `35265040415`; artifact `10516435782`; 8/8 rendered and decoded; French lock PASS.
- Sunday final worker SHA `797c7ffde0fc44d7af869e70b9d2e74d6fcd87fb`; run `35271641904`; artifact `10519381359`; 9/9 rendered and decoded; French lock PASS.
- Audio Engine pin remains `3392d4f22f0a9b054a05b5c05a7856985c0ab030`, version `0.9.2`, voice `narrateur-vif`, language `fr-FR`.
- Optional-depth audio = 0/12, disposition `DEFERRED_UNTIL_COORDINATION_ACCEPTS`.

### J5 — Independent qualification

Latest independent audit on candidate `ba6e262fd27c570214d167d5df3e60a1e054d95c` returned `HOLD`, `FAIL count = 0`.

All content/audio invariants passed. J5 reduced the remaining release gap to three runtime roots:

1. V2 `series.json` absent;
2. V2 `assets/visit-experience.json` absent;
3. no durable executable materialization of the 25 already-qualified primary MP3 bytes.

J5 did not repair anything.

### J6 — V2 Runtime Materialization

PASS / ACCEPTED / INTEGRATED from worker SHA `d5fdc2fc73a105e67d3db2048a458187d4704ea3`, based exactly on coordination baseline `2affe9b8dbdb78d33578d70f9b96cdbd92b76ece` (`ahead_by=4`, `behind_by=0`).

J6 closes all three J5 runtime-root HOLDs materially:

- added `series/seville-discovery-v2/series.json` with exactly 25 accepted primary runtime episodes;
- added `series/seville-discovery-v2/assets/visit-experience.json` with `audio_first_field_ui` v2 and V1 fallback;
- promoted the exact J4-qualified bytes into durable Git-backed `series/seville-discovery-v2/assets/audio/<SCENE_ID>/` packages;
- added `runtime-audio-manifest.json` with `status=QUALIFIED_BYTES_PROMOTED`, `scene_count=25`, `hash_match_count=25`;
- changed `site/build.py` only to support hash-locked packaged audio publication before any generated-audio fallback;
- build output proved executable V2 paths under `dist/s/seville-discovery-v2/` and `dist/data/seville-discovery-v2/`;
- exact MP3 identity = 25/25 against accepted J4 hashes; no Edge TTS rerender occurred;
- City Guide Factory gate run `35277970065` on final worker SHA = SUCCESS;
- V1_CHANGED_FILES = 0.

J6 draft PR #222 remains a worker-only draft and MUST NOT be merged to `main`.

## J7 — Sound Direction Registry Reconciliation

PASS / ACCEPTED / INTEGRATED from worker SHA `4aea6feab235aeef6576844c05f42868b947fdb2`, based exactly on coordination baseline `4ac8b3151baf5ad39a3971ab1d42b35750fec3db` (`ahead_by=1`, `behind_by=0`).

- bounded diff = exactly `series/sound-direction-catalog.json` and `series/sound-direction-review-v1.json`;
- `seville-discovery-v2` registered as `mode=visit`, `default_density=none`, preserving real-city-first / no artificial ambience direction;
- all 25 real V2 program IDs registered as `density=none`, `decision=keep`;
- exact J7 validator evidence: GitHub Actions run `35316841309`, job `validate-j7`, exact checkout of `4aea6fea...`, `python tools/sound_direction.py validate` = PASS;
- validator reported catalogue/review consistency and detailed Sound Direction coverage PASS;
- worker PR #223 remains unmerged and registry-only;
- no MP3, J2, J3, J4, J6 runtime or V1 path changed;
- `V1_CHANGED_FILES = 0`.

The earlier J7 `HOLD_EVIDENCE_ONLY` is closed. No J7 blocker remains.

## Final qualification step

There is no further planned build worker before release qualification.

Rebind J5 to the current coordination candidate and run strict `/refresh -> /audit` only. J5 must independently revalidate the fully integrated J1–J7 candidate, including runtime routes/fallback/player/resume/offline/MediaSession, durable 25/25 audio identity, Sound Direction registry consistency, non-V2 regression and `V1_CHANGED_FILES = 0`.

J5 owns the final `V2_READY` verdict and must not repair any defect it finds.

## Immutable / carried-forward constraints

- `V1_CHANGED_FILES = 0` mandatory.
- V1 defects remain frozen and must not be repaired in `series/seville-discovery/**`.
- Friday/Saturday/Sunday scene programs remain editorial authority.
- J4 exact primary MP3 bytes are now durable and must not be rerendered or replaced.
- Optional-depth audio stays deferred 0/12.
- Casa de Pilatos stays fallback-only.
- Sunday airport exit remains protected.
- No geofencing requirement.
- `COMMIT_EXISTS != INTEGRATED` and `WORKER_PASS != RELEASE_PASS`.
- no human audio gate.

The coordinating discussion owns integration order, conflict arbitration and current project HEAD knowledge. This file is a coordination pointer, not a substitute for fresh Git ref or kernel-authority checks.
