# Séville Field Guide V2 — Coordination Head

Status: ACTIVE_BOOTSTRAP

Integration branch: `seville-field-guide-v2`
Frozen V1 path: `series/seville-discovery/**`
V2 path: `series/seville-discovery-v2/**`

Immediate parallel workers:

- J1 FIELD STORY RESEARCH -> branch `seville-v2-j1-field-research`
- J3 AUDIO-FIRST UX -> branch `seville-v2-j3-audio-first-ux`

Coordination rules:

- worker branches do not merge each other;
- workers return durable Git evidence to the coordinating discussion;
- coordination revalidates current integration HEAD before every cherry-pick/merge/integration mutation;
- J1 must not mutate UX or V1;
- J3 must not mutate V1 or production audio/narrative content;
- J2 starts progressively from bounded J1 outputs after first research batch;
- J4 starts from J2 scene batches;
- J5 remains independent and may not repair defects it detects in the same qualification job;
- no human audio gate;
- `V1_CHANGED_FILES = 0` is mandatory.

The coordinating discussion owns integration order, conflict arbitration and current HEAD. This file is a coordination pointer, not a substitute for Git ref freshness checks.
