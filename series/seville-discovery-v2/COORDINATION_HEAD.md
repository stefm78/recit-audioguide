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
- J1 FIELD STORY RESEARCH — Sunday batch PASS and ACCEPTED from worker SHA `4ca3af65748cd240025ae9e556850d48a4ace05a`, integrated by fast-forward from coordination HEAD `dff97fabb6912e67f5b404bf1d617858c42ba6c9`; artifacts: `research/SUNDAY_FIELD_STORY_RESEARCH.md`, `research/SUNDAY_SOURCE_MANIFEST.md`, and `research/SUNDAY_BUILD_PROVENANCE.md`. Primary Sunday remains Maestranza -> checkout / Lockers Agua -> Museo de Bellas Artes -> protected airport departure; Casa de Pilatos remains fallback-only.
- J2 FIELD SHOWRUNNER — Friday batch PASS and ACCEPTED from worker SHA `4f7d7f3dace0890274acc5470bf76e5ac6f9d3d3`; integrated through merge commit `7bd26fee6aeaf2f3c7cc7f6cbd104d46fdda081d`; artifact: `scenes/FRIDAY_MORNING_SCENE_PROGRAM.json`, 8 primary scenes + 3 optional-depth units + 2 intentional silence dispositions.
- J2 FIELD SHOWRUNNER — Saturday batch PASS and ACCEPTED from worker SHA `9fa00643e7ac74f324dd2947ba9b09d785e5e842`; integrated by fast-forward from coordination baseline `d3a78890aae5213d42676cd95ec9829015b7d82d`; artifact: `scenes/SATURDAY_SCENE_PROGRAM.json`, 8 primary scenes + 5 optional-depth units + 3 intentional silence windows.
- J2 FIELD SHOWRUNNER — Sunday batch PASS and ACCEPTED from worker SHA `19c70040429d1dffc106f94ffd7dde3654477232`, integrated by fast-forward from coordination HEAD `c7d86659c39eb525b6219aea545f74379606619c`; artifact: `scenes/SUNDAY_SCENE_PROGRAM.json`, 9 primary scenes + 4 optional-depth units + 4 intentional silence dispositions. Protected Sunday constraints remain intact: Maestranza primary, checkout/Lockers silence-logistics, Bellas Artes primary, Pilatos fallback-only, protected airport exit.
- J3 AUDIO-FIRST UX — PASS on worker scope and integrated from worker SHA `ae64ce952100d5dacf676de968451723b830b4bb` through merge/integration commit `6e3c9e034a4c922b0dc97accb733e1355e5a72f4`.
- J3 integrated blobs are exact worker-final identities: `AUDIO_FIRST_UX_CAPABILITY.json` = `85f2dd0a4ba49a9c7e4d0512c331bed151a46c21`; `tests/test_seville_v2_audio_first_ux.py` = `1762a12e227c3db52b1cc4cb0ffbb76237379def`; `web/next-step.js` = `82b330a9a88c56d71c4d7f3f26ad506f7dd1c565`.
- J4 AUDIO PRODUCTION — Friday Morning PASS and ACCEPTED from worker final SHA `06ce0580fade766f8a4bfe0dd0e8721899b0d3b6`; qualified assets were produced from SHA `c91484167544a10e76e46a4588d556bb16a3c360` and integrated with Saturday J2 state through merge commit `8259e477955c4a542235f190dc6d71acbc3798e0`.
- J4 Friday durable evidence: `audio/FRIDAY_MORNING_AUDIO_MANIFEST.json`, eight `audio/SEV2-FRI-AM-*.json` programs, `qualification/J4_FRIDAY_MORNING_AUDIO_QUALIFICATION.json`, and `tests/test_seville_v2_friday_audio_production.py`. Qualified workflow run `35260567914` = SUCCESS; artifact `10514517681` = `seville-v2-j4-friday-audio`, 2,578,475 bytes, digest `sha256:d7019aae1edad6a41ae25aa96fd7ad5a38cb2b4ea53058b758d86db1f721b61f`.
- J4 Friday primary contract = 8 expected / 8 rendered / 8 decoded / 0 missing / 0 failed, French lock PASS, pinned Audio Engine `3392d4f22f0a9b054a05b5c05a7856985c0ab030` (`0.9.2`, `narrateur-vif`, `fr-FR`). Optional-depth D01-D03 remain intentionally deferred.
- J4 AUDIO PRODUCTION — Saturday PASS and ACCEPTED from worker final SHA `8fd82f816430a6fd77d0209a808d90e1af9ee0ad`; qualified assets were produced from SHA `fa4a25022763bbd22077135a706b3e2c48b2bfbb` and integrated by fast-forward from coordination candidate `3c5b0418f112616a40c62ec1ffe964d4a5b85ec2`.
- J4 Saturday durable evidence: `audio/SATURDAY_AUDIO_MANIFEST.json`, eight `audio/SEV2-SAT-*.json` programs, `qualification/J4_SATURDAY_AUDIO_QUALIFICATION.json`, and `tests/test_seville_v2_saturday_audio_production.py`. Qualified workflow run `35265040415` = SUCCESS; artifact `10516435782` = `seville-v2-j4-saturday-audio`, 2,719,972 bytes, digest `sha256:ee186e2d4ea0eff7b36e16fa1c66a27b24fdfb9c666c4fe10f502d64fd28c981`.
- J4 Saturday primary contract = 8 expected / 8 rendered / 8 decoded / 0 missing / 0 failed, French lock PASS, same pinned engine/preset/language as Friday. Optional-depth 0/5 remains `DEFERRED_UNTIL_COORDINATION_ACCEPTS`.
- J5 AUTOMATED QUALIFICATION — first independent pass on candidate `3c5b0418f112616a40c62ec1ffe964d4a5b85ec2` returned `HOLD`, not `FAIL`: all applicable Friday and static UX/V1 invariants passed; HOLD reasons were missing Saturday audio, missing Sunday content/audio, and missing executable V2 runtime materialization for causal player/resume/offline/screen-lock/MediaSession/fallback/route E2E proof. J5 performed no repair mutation. Saturday-audio absence has since been resolved; Sunday scene content is now resolved; Sunday audio and executable runtime evidence remain pending.

## Active / next workers

- J1 FIELD STORY RESEARCH -> COMPLETE / INTEGRATED for Friday, Saturday and Sunday. No further research action unless a downstream worker identifies a material factual/source gap that accepted evidence cannot resolve.
- J2 FIELD SHOWRUNNER -> COMPLETE / INTEGRATED for Friday, Saturday and Sunday. No further showrunner action unless J4 or J5 returns an owner-specific defect.
- J3 AUDIO-FIRST UX -> COMPLETE / INTEGRATED; no further worker action unless integration or J5 finds a regression owned by J3.
- J4 AUDIO PRODUCTION -> Friday and Saturday are COMPLETE / INTEGRATED. Sunday scene program is now ACCEPTED; rebind J4 to the current integration HEAD, restart from `/refresh`, and produce only the nine accepted Sunday primary scenes. Keep all four optional-depth assets deferred unless coordination explicitly changes that decision.
- J5 AUTOMATED QUALIFICATION -> prior audit = HOLD on older candidate `3c5b0418f112616a40c62ec1ffe964d4a5b85ec2`. Do not rerun merely for J2 Sunday. Next high-value rerun is after J4 Sunday integration and/or executable V2 runtime materialization; use strict `/refresh -> /audit` and no repair.

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
- Friday, Saturday and Sunday J2 programs share the same runtime/audio mapping contract and require no geofencing.
- Sunday research uses a dedicated `SUNDAY_SOURCE_MANIFEST.md`; source traceability to that accepted evidence must be preserved and Pilatos must remain fallback-only.
- Sunday J2 accepted contract includes 9 primary scenes, 4 optional-depth units, 4 intentional silence dispositions and a protected exit where airport timing overrides further cultural content.
- Successful render/decode artifacts are production evidence, not by themselves proof of app-level offline, resume, MediaSession or lock-screen behavior; those remain J5 integration invariants when the necessary runtime materialization exists.
- Qualified Friday/Saturday MP3s currently live in time-limited GitHub Actions artifacts; release readiness requires durable runtime-consumable publication or an equivalent reproducible materialization before those artifacts expire.

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
