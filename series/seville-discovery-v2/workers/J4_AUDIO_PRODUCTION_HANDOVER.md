# J4 — AUDIO PRODUCTION — Worker Handover

## Mission

Produce deterministic V2 audio assets from J2 scene batches and integrate them into the existing audio/runtime architecture without changing route, UX ownership or frozen V1 content.

## Kernel execution contract

This is a governed worker job. Use the ACTIVE kernel primitives only when causally required.

Default execution path:

`/refresh -> /solve -> /build -> /audit`

Use `/research` only for a production-blocking technical ambiguity that cannot be resolved from the repository and existing pipeline evidence. Do not reopen editorial research.

Primitive responsibilities:

- `/refresh` — revalidate kernel authority, worker branch HEAD, V2 contract, V1 frozen baseline and the exact J2 scene batch accepted by coordination.
- `/solve` — decide bounded production segmentation, manifest mapping, reuse of the existing audio pipeline and the cheapest implementation path that preserves current offline/background capabilities. Do not materially rewrite J2 scenes.
- `/build` — render/materialize deterministic scene assets and manifests and integrate only the minimum V2 production/runtime data required.
- `/audit` — verify expected/produced scene counts, failed renders, manifest integrity, French lock, deterministic IDs/hashes, playback integration and `V1_CHANGED_FILES = 0`.

Re-enter only the smallest failed causal stage: production-plan defect -> `/solve`; implementation/render defect -> `/build`; then `/audit` again. Return editorial defects to J2 rather than silently changing content.

`/learn` is optional and only for a reusable audio-production lesson beyond this job.

## Preconditions

Consume only J2 scene batches that coordination identifies as ready for production. Do not invent or materially rewrite scene content to compensate for editorial gaps; report those back to J2.

## Requirements

- French-only output consistent with existing French lock expectations.
- Scene-level assets/manifests suitable for `J'y suis`, `Continuer`, optional depth and resume semantics.
- Fast start and prefetch-friendly segmentation.
- Preserve offline and lock-screen/background playback capabilities already qualified by the product where applicable.
- Preserve deterministic mapping `scene_id -> produced asset -> manifest identity`.
- No decorative ambience by default; add none unless a separate explicit sound-direction decision authorizes it.
- No human audio gate.

## Boundaries

- no modification below `series/seville-discovery/**`;
- no route, booking or logistics changes;
- no primary UX redesign;
- no historical research beyond resolving a production-blocking ambiguity;
- do not silently change J2 text to fit a voice engine.

## Automated evidence

Return at minimum:

- branch/ref and final commit SHA;
- exact changed paths;
- kernel path actually used and any local re-entry;
- produced scene count / expected scene count;
- missing/failed renders;
- manifest validation;
- French lock result;
- deterministic IDs/hashes where the pipeline supports them;
- playback integration tests relevant to scene segmentation;
- `/audit` verdict and unresolved blockers.

A production error is a technical blocker, not a request for human artistic approval.
