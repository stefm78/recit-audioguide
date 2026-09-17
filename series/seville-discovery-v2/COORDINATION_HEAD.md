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

For read-only status checks, `/refresh` may be sufficient. Do not run primitives merely for ceremony; re-enter only the smallest causally affected stage.

## Integrated evidence

- J1 FIELD STORY RESEARCH — Friday batch ACCEPTED and integrated from worker SHA `0d131065708cedc6853dc1c844cd0cfd50473441`; artifacts: `research/FRIDAY_MORNING_FIELD_STORY_RESEARCH.md` and initial `research/SOURCE_MANIFEST.md`.
- J1 FIELD STORY RESEARCH — Saturday batch ACCEPTED from worker SHA `ab368ca8225e4e87fd29976637608a10adcf5812` and integrated through merge commit `670994dc6d4735255aa7d5db34ba518db35d94ca`; artifacts: `research/SATURDAY_FIELD_STORY_RESEARCH.md` and enriched `research/SOURCE_MANIFEST.md`.
- J2 FIELD SHOWRUNNER — Friday batch PASS and ACCEPTED from worker SHA `4f7d7f3dace0890274acc5470bf76e5ac6f9d3d3`; integrated through merge commit `7bd26fee6aeaf2f3c7cc7f6cbd104d46fdda081d`; artifact: `scenes/FRIDAY_MORNING_SCENE_PROGRAM.json`, 8 primary scenes + 3 optional-depth units + 2 intentional silence dispositions.
- J2 FIELD SHOWRUNNER — Saturday batch PASS and ACCEPTED from worker SHA `9fa00643e7ac74f324dd2947ba9b09d785e5e842`; integrated by fast-forward from coordination baseline `d3a78890aae5213d42676cd95ec9829015b7d82d`; artifact: `scenes/SATURDAY_SCENE_PROGRAM.json`, 8 primary scenes + 5 optional-depth units + 3 intentional silence windows.
- J3 AUDIO-FIRST UX — PASS on worker scope and integrated from worker SHA `ae64ce952100d5dacf676de968451723b830b4bb` through merge/integration commit `6e3c9e034a4c922b0dc97accb733e1355e5a72f4`.
- J3 integrated blobs are exact worker-final identities: `AUDIO_FIRST_UX_CAPABILITY.json` = `85f2dd0a4ba49a9c7e4d0512c331bed151a46c21`; `tests/test_seville_v2_audio_first_ux.py` = `1762a12e227c3db52b1cc4cb0ffbb76237379def`; `web/next-step.js` = `82b330a9a88c56d71c4d7f3f26ad506f7dd1c565`.

## Active / next workers

- J1 FIELD STORY RESEARCH -> branch `seville-v2-j1-field-research`; active bounded batch is Sunday: Maestranza -> checkout / Lockers Agua -> Museo de Bellas Artes -> protected airport departure. Casa de Pilatos remains fallback only.
- J2 FIELD SHOWRUNNER -> branch `seville-v2-j2-field-showrunner`; Friday and Saturday are COMPLETE / INTEGRATED. Do not start Sunday until J1 Sunday research is ACCEPTED by coordination; before Sunday work, rebind to the then-current integration HEAD and restart from `/refresh`.
- J3 AUDIO-FIRST UX -> COMPLETE / INTEGRATED; no further worker action unless integration or J5 finds a regression owned by J3.
- J4 AUDIO PRODUCTION -> branch `seville-v2-j4-audio-production`; first bounded batch remains Friday only, consuming `scenes/FRIDAY_MORNING_SCENE_PROGRAM.json`. Do not widen its active scope to Saturday until Friday production returns PASS and is integrated. Saturday scene production is queued next.
- J5 AUTOMATED QUALIFICATION -> branch `seville-v2-j5-automated-qualification` remains PREPARED_ONLY; do not launch qualification until J4 Friday production is integrated. Before launch, rebind J5 to the then-current integration HEAD and run `/refresh -> /audit` only.

## Reported V1 defects — do not repair in frozen fallback

Saturday J1 reported two stale narrative references in frozen V1. They are coordination-known defects and must be corrected in V2 content, not by mutating V1:

- Plaza de España audio says `demain à Triana`, but Triana occurs on Friday before Saturday. Saturday V2 scene content now correctly says `Hier, à Triana`.
- Archivo audio announces for Sunday `un palais privé puis la peinture`, but Sunday primary is now Maestranza then Bellas Artes; Casa de Pilatos is fallback only. Saturday V2 close now announces Maestranza then Sevillian painting.

## Integration constraints now carried forward

- Future V2 `visit-experience.json` must include the `capabilities.audio_first_field_ui` fragment declared by `AUDIO_FIRST_UX_CAPABILITY.json`.
- Each V2 episode intended for the field controller must have a matching `experience.episodes` entry; `look_first` is preferred for the concise field cue.
- Shared `web/next-step.js` capability guard and legacy `firstPendingIndex` semantics must be preserved by any later integration touching that file.
- J3 deliberately does not own `web/app.js`, audio source assignment, direct playback, resume, MediaSession, offline or lock-screen mechanics; those remain shared runtime responsibilities and require integration-level qualification once V2 content/audio exist.
- J4 must preserve the accepted J2 text and deterministic `scene_id -> asset -> manifest` mapping; editorial defects return to J2 instead of being silently rewritten during production.
- Friday and Saturday J2 programs share the same runtime/audio mapping contract and require no geofencing.

## Coordination rules

- worker branches do not merge each other;
- workers return durable Git evidence to the coordinating discussion;
- coordination revalidates current integration HEAD before every cherry-pick/merge/integration mutation;
- worker completion requires its handover-defined `/audit` result, not merely a commit;
- J1 must not mutate UX or V1;
- J3 must not mutate V1 or production audio/narrative content;
- J2 starts progressively from bounded J1 outputs after accepted research batches;
- J4 starts progressively from accepted J2 scene batches;
- J5 runs `/refresh -> /audit`, remains independent and may not repair defects it detects in the same qualification job;
- no human audio gate;
- `V1_CHANGED_FILES = 0` is mandatory;
- `COMMIT_EXISTS != INTEGRATED` and `WORKER_PASS != RELEASE_PASS`;
- integration evidence must always name exact worker SHA and integration SHA.

The coordinating discussion owns integration order, conflict arbitration and current project HEAD knowledge. This file is a coordination pointer, not a substitute for Git ref freshness checks or kernel authority.
