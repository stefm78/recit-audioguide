# Séville Field Guide V2 — Coordination Head

Status: ACTIVE_BOOTSTRAP

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

For read-only status checks, `/refresh` may be sufficient. Do not run primitives merely for ceremony; re-enter only the smallest causally affected stage.

## Immediate parallel workers

- J1 FIELD STORY RESEARCH -> branch `seville-v2-j1-field-research`
- J3 AUDIO-FIRST UX -> branch `seville-v2-j3-audio-first-ux`

Both worker handovers are kernel-native and define their own primitive pipelines. Worker conversations must execute the handover rather than replace it with an ad-hoc prompt.

## Prepared but not launched yet

- J2 FIELD SHOWRUNNER -> start progressively from accepted J1 batches;
- J4 AUDIO PRODUCTION -> start from J2 scene batches;
- J5 AUTOMATED QUALIFICATION -> create from the then-current integration HEAD so it qualifies the real candidate rather than a stale bootstrap branch.

## Coordination rules

- worker branches do not merge each other;
- workers return durable Git evidence to the coordinating discussion;
- coordination revalidates current integration HEAD before every cherry-pick/merge/integration mutation;
- worker completion requires its handover-defined `/audit` result, not merely a commit;
- J1 must not mutate UX or V1;
- J3 must not mutate V1 or production audio/narrative content;
- J2 starts progressively from bounded J1 outputs after first research batch;
- J4 starts from J2 scene batches;
- J5 runs `/refresh -> /audit`, remains independent and may not repair defects it detects in the same qualification job;
- no human audio gate;
- `V1_CHANGED_FILES = 0` is mandatory;
- `COMMIT_EXISTS != INTEGRATED` and `WORKER_PASS != RELEASE_PASS`;
- integration evidence must always name exact worker SHA and integration SHA.

The coordinating discussion owns integration order, conflict arbitration and current project HEAD knowledge. This file is a coordination pointer, not a substitute for Git ref freshness checks or kernel authority.
