# J6 — V2 Runtime Materialization

Status: READY
Role: runtime/release integration worker
Branch: `seville-v2-j6-runtime-materialization`

## Mission

Materialize the already-accepted Séville V2 content, audio-first UX contract and qualified primary audio into one executable V2 runtime surface, without changing V1 and without reopening editorial/audio-production decisions.

This job exists to close the three root HOLDs isolated by J5:

1. runtime descriptor absent;
2. audio-first experience binding absent;
3. durable executable materialization absent.

## Authoritative inputs

Consume the current integration candidate and these accepted V2 authorities:

- `series/seville-discovery-v2/FIELD_GUIDE_V2_CONTRACT.md`
- `series/seville-discovery-v2/AUDIO_FIRST_UX_CAPABILITY.json`
- `series/seville-discovery-v2/scenes/FRIDAY_MORNING_SCENE_PROGRAM.json`
- `series/seville-discovery-v2/scenes/SATURDAY_SCENE_PROGRAM.json`
- `series/seville-discovery-v2/scenes/SUNDAY_SCENE_PROGRAM.json`
- `series/seville-discovery-v2/audio/FRIDAY_MORNING_AUDIO_MANIFEST.json`
- `series/seville-discovery-v2/audio/SATURDAY_AUDIO_MANIFEST.json`
- `series/seville-discovery-v2/audio/SUNDAY_AUDIO_MANIFEST.json`
- the three J4 qualification JSON files
- existing builder/runtime/player/offline/Pages implementation only as needed to materialize V2.

Do not mutate `series/seville-discovery/**`.

## Required kernel path

Default:

`/refresh -> /research -> /solve -> /build -> /audit`

- `/refresh`: rebind current control-plane authority, worker branch, integration HEAD, V2 contract and J5 HOLD evidence.
- `/research`: inspect only the smallest existing builder/runtime/player/Pages surfaces required to understand series packaging, `visit-experience`, audio publication, offline packaging, fallback, resume and MediaSession. Do not reopen content research.
- `/solve`: choose the smallest architecture that closes all three root HOLDs. Prefer reuse of the current builder/runtime over new machinery.
- `/build`: materialize the runtime and durable exact audio publication needed for an executable V2.
- `/audit`: prove structure, exact audio identity, build output and non-regression. Re-enter only the smallest causally affected stage.

## Required outputs

At minimum, produce:

1. `series/seville-discovery-v2/series.json`
   - executable V2 series descriptor;
   - all 25 accepted primary scene IDs represented exactly once as runtime episodes/items as required by the existing schema;
   - valid `maps_url` / routing data derived from accepted route authorities;
   - IDs aligned exactly with J2/J4 scene/program identities;
   - no primary Casa de Pilatos route; Sunday remains Maestranza -> logistics silence -> Bellas Artes -> protected airport exit.

2. `series/seville-discovery-v2/assets/visit-experience.json`
   - `capabilities.audio_first_field_ui.enabled = true`;
   - version compatible with the accepted J3 capability contract;
   - `classic_fallback_url = "../seville-discovery/"`;
   - one matching experience entry for every V2 scene intended for the field controller;
   - concise field cues; no re-expansion into article-first UX.

3. durable executable audio materialization
   - publish the 25 already-qualified primary MP3 bytes into the source/build path used by the executable V2;
   - preserve exact J4-qualified MP3 SHA-256 identities whenever possible;
   - include the corresponding renderer manifests/transcripts needed by the existing runtime/build contract;
   - do not produce optional-depth audio: 0/12 remains `DEFERRED_UNTIL_COORDINATION_ACCEPTS`.

4. executable build evidence
   - materialize `dist/s/seville-discovery-v2/index.html`;
   - materialize `dist/data/seville-discovery-v2/series.json`;
   - materialize `dist/data/seville-discovery-v2/assets/visit-experience.json`;
   - materialize all 25 primary audio assets under the runtime URL layout actually consumed by the app;
   - prove the builder injected/resolved `audio_url` and transcript references correctly.

## Audio identity rule

The preferred solution is promotion of the exact MP3 bytes already qualified by J4.

J4 qualified audio was produced through a remote TTS provider, so a fresh render is **not** automatically equivalent. If any MP3 is re-rendered instead of promoted byte-for-byte, treat it as new audio evidence and require new hash/decode qualification before claiming closure.

The final `/audit` must compare the actually published/runtime MP3 SHA-256 values against the accepted J4 qualification hashes and report exact match counts.

## Scope constraints

- `V1_CHANGED_FILES = 0` mandatory.
- Do not change J1 research, J2 spoken text, J2 scene ordering, J4 voice/preset/language or optional-depth disposition.
- Do not redesign J3 UX.
- Shared runtime/build code may change only when strictly required for V2 materialization and must remain capability-gated / non-V2 safe.
- No geofencing requirement.
- No merge to `main`.
- No human audio gate.

## Qualification target

J6 does not declare `V2_READY`; J5 owns final independent qualification.

J6 should make the following previously untestable invariants executable for J5:

- route links;
- V1 fallback navigation;
- player with V2 `audio_url`;
- save/reload/resume;
- offline playback/package behavior;
- screen-lock / MediaSession where supported;
- non-V2 runtime regression;
- durable publication of all 25 primary MP3 assets.

## Stop condition

Stop when one bounded worker candidate contains the runtime descriptors, durable audio materialization and a successful executable V2 build with enough deterministic evidence for J5 to rerun `/refresh -> /audit` independently.

Return:

- final commit SHA and branch;
- changed paths grouped as V2 descriptors / durable audio / shared build-runtime / tests-evidence;
- exact 25/25 audio publication hash comparison against J4;
- build command/workflow and result;
- generated runtime paths and episode counts;
- route/fallback/player/resume/offline/MediaSession evidence obtainable inside J6;
- `V1_CHANGED_FILES` and non-V2 regression evidence;
- `/audit` verdict and remaining blockers;
- no merge.
