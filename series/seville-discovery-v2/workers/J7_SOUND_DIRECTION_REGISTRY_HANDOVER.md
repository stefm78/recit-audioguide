# J7 — Sound Direction Registry Reconciliation

Status: READY
Role: bounded registry-consistency worker
Branch: `seville-v2-j7-sound-direction-registry`

## Mission

Close the single transverse Sound Direction registry blocker exposed after J6 made Séville V2 a real executable series.

This is a registry reconciliation job, not a new sound-design job.

Do not reopen narrative, voice, ambience, audio production, runtime architecture or V1.

## Authoritative baseline

Start from the current `seville-field-guide-v2` integration HEAD prepared by coordination after J6 acceptance.

Accepted facts that MUST NOT be changed:

- `seville-discovery-v2` is a real visit series with 25 primary audio programs;
- Friday 8 + Saturday 8 + Sunday 9 = 25 primary programs;
- all 25 exact MP3 bytes are already J4-qualified and J6-promoted durably;
- J4 declared `decorative_ambience = NONE` and `return_bridge_audio = NONE`;
- optional-depth audio remains 0/12 `DEFERRED_UNTIL_COORDINATION_ACCEPTS`;
- the Seville direction principle remains real-city-first / no fake city ambience / no decorative flamenco cues / no continuous music;
- `V1_CHANGED_FILES = 0` is mandatory.

## Required kernel path

Default:

`/refresh -> /solve -> /build -> /audit`

Use `/research` only if the existing validator/schema is genuinely ambiguous after inspecting the local repository. Do not perform editorial or audio research.

### /refresh

Rebind:

- ACTIVE kernel authority;
- worker branch;
- current integration HEAD;
- J6 accepted runtime candidate;
- `series/sound-direction-catalog.json`;
- `series/sound-direction-review-v1.json`;
- `tools/sound_direction.py` validator contract;
- relevant Pages/change-aware workflow logic only as needed to validate the diff correctly.

### /solve

Choose the smallest registry-only reconciliation that satisfies the existing Sound Direction validator while preserving all accepted Seville V2 decisions.

Default expected solution unless repository evidence contradicts it:

1. add one catalog entry for `seville-discovery-v2` using visit mode, default density `none`, and the already accepted real-city-first/no-decorative-sound principle;
2. add exactly 25 review entries for the real program IDs:
   - `SEV2-FRI-AM-01` .. `SEV2-FRI-AM-08`;
   - `SEV2-SAT-01` .. `SEV2-SAT-08`;
   - `SEV2-SUN-01` .. `SEV2-SUN-09`;
3. use `density: "none"` and `decision: "keep"` for those 25 entries unless the existing schema/validator requires a different registry-only representation.

Do not create detailed direction sidecars unless the validator contract strictly requires them; `density=none` / `decision=keep` should not invent sound work.

### /build

Mutate only the minimum registry/test surface required.

Expected writable paths:

- `series/sound-direction-catalog.json`;
- `series/sound-direction-review-v1.json`;
- tests/evidence only if strictly needed to prove the reconciliation.

Forbidden mutations:

- any `series/seville-discovery/**` path;
- any V2 MP3/manifest/transcript;
- any J2 scene program or spoken text;
- any J4 audio program/qualification;
- `web/next-step.js` or J3 capability;
- `series/seville-discovery-v2/series.json` or `assets/visit-experience.json` unless an actual validator defect proves a registry reference typo, in which case STOP and return ownership to coordination instead of silently changing runtime;
- `site/build.py` unless a genuine independent validator defect is proven; do not use shared-code mutation to bypass the registry requirement.

If a PR is needed to exercise CI, target `seville-field-guide-v2` as its base, not `main`, so the worker diff contains only this bounded reconciliation and already-integrated J4/J6 audio is not misclassified as fresh audio work.

### /audit

Prove at minimum:

- `python tools/sound_direction.py validate` PASS;
- `seville-discovery-v2` exists exactly once in the catalog;
- all 25 and only the 25 accepted primary program IDs are added to the review for this V2 batch;
- each added V2 entry preserves the accepted no-new-sound decision;
- no MP3 bytes changed;
- no V1 path changed;
- J6 runtime descriptors and hash-locked audio manifest remain byte-identical to baseline;
- relevant City Guide / Pages gates pass in the correct integration-relative diff context, or return the exact smallest remaining non-registry blocker.

## Stop condition

Stop when the Sound Direction registry validator passes and the bounded candidate contains no audio/editorial/runtime mutation beyond the required registry reconciliation.

Return:

- final SHA and branch;
- exact changed paths;
- catalog entry added;
- count/list of review entries added;
- validator command/result;
- CI/workflow evidence;
- `V1_CHANGED_FILES`;
- proof J6 runtime/audio identities remained unchanged;
- `/audit` verdict;
- remaining blockers, if any;
- no merge.

J7 does not declare `V2_READY`. After J7 integration, J5 must run a fresh independent `/refresh -> /audit` and owns the final release verdict.
