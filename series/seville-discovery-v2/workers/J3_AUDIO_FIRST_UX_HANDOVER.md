# J3 — AUDIO-FIRST UX — Worker Handover

## Mission

Turn the Seville V2 field experience into an audio-guide controller rather than a page to read, while preserving all non-V2 behavior and the frozen V1 fallback.

## Kernel execution contract

This is a governed worker job. Use the ACTIVE kernel primitives causally.

Default execution path:

`/refresh -> /research -> /solve -> /build -> /audit`

Primitive responsibilities:

- `/refresh` — revalidate kernel authority, worker branch HEAD, V2 contract, V1 frozen baseline and the current shared Web/player architecture before mutation.
- `/research` — inspect the smallest causal UX/runtime working set: `web/next-step.js`, relevant render/player/resume code, existing tests and current mobile behavior. Do not perform repository-wide discovery without a causal need.
- `/solve` — choose the smallest architecture that produces a true audio-first V2 visit mode, preserves non-V2 behavior and keeps V1 fallback immediately reachable. Challenge solutions that merely hide the current article-like page inside accordions.
- `/build` — implement only the selected V2 capability/schema and the minimum guarded shared-code changes required by that decision.
- `/audit` — prove text-budget compliance, fallback reachability, resume/current-step semantics, accessibility/mobile usability, non-V2 regression safety and `V1_CHANGED_FILES = 0`.

Re-enter only the smallest failed causal stage: architectural premise/UX decision defect -> `/solve`; missing current-state evidence -> `/research`; implementation defect -> `/build`; then `/audit` again.

`/learn` is optional and only for a reusable product pattern beyond Seville. It must not become authority for this implementation.

## Read first

- `series/seville-discovery-v2/FIELD_GUIDE_V2_CONTRACT.md`
- `series/seville-discovery-v2/BASELINE_V1_FALLBACK.md`
- current `web/next-step.js`, series rendering/player code and existing Android/Web visit behavior.

## Product target

Normal V2 visit mode should keep the visitor's eyes on Seville and use the phone only to control the guide.

Primary surface should contain approximately:

- `step / total`;
- short place/action title;
- one concise observation cue;
- prominent Play/Pause;
- `Itinéraire`, `J'y suis`, `Continuer`.

Secondary/overflow surface should contain:

- `Je ne trouve pas`;
- `Approfondir`;
- `Transcription`;
- `Sources`;
- `Toutes les étapes`;
- `Version classique V1`.

Planning/preparation mode may remain information-rich. Visit mode must not repeat `why`, `look`, field-program prose and next-step paragraphs in the primary flow.

## Scope boundaries

You may:

- add V2-only UI/runtime code;
- change shared web code only behind an explicit V2 capability/schema guard so existing series render unchanged;
- define a minimal V2 visit schema needed by the UI;
- add automated UI/structural tests;
- make the V1 fallback reachable from the V2 visit surface.

You must not:

- modify any file under `series/seville-discovery/**`;
- rewrite historical/narrative content;
- generate production audio;
- change route/bookings/logistics;
- introduce a human audio gate;
- regress current Library/resume semantics for other series.

## Design challenge

Do not merely hide the current long page inside accordions. Re-evaluate the information hierarchy around the field task. The expected mental model is a remote control for an audio guide, not an article with audio attached.

Prefer progressive disclosure and stateful actions. Preserve accessibility, large touch targets, screen-reader semantics and current completion/resume behavior.

## Qualification

At minimum prove:

- non-V2 series output unchanged or intentionally equivalent;
- V1 Seville content unchanged;
- V2 primary visit surface meets a bounded text budget;
- V1 fallback action is reachable;
- current-step/resume semantics remain correct;
- mobile-width rendering remains usable;
- no dependency on precise location is required for basic operation.

No human audio gate.

## Deliverable

Work on a dedicated worker branch.

Return:

- branch/ref and final commit SHA;
- exact changed paths;
- kernel path actually used and any local re-entry;
- screenshots or deterministic DOM/test evidence where available;
- test results and `/audit` verdict;
- explicit non-V2 and V1 non-regression evidence;
- integration assumptions needed by J2/J4.
