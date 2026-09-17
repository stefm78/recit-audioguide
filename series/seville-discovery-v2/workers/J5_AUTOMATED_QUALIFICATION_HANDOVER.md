# J5 — AUTOMATED QUALIFICATION — Worker Handover

## Mission

Independently prove or refute the Seville V2 release invariants. Do not repair defects in the same qualification job.

## Kernel execution contract

This is an independent governed qualification job.

Required execution path:

`/refresh -> /audit`

Primitive responsibilities:

- `/refresh` — revalidate kernel authority, candidate branch/ref/SHA, V2 contract, V1 frozen baseline and currently applicable qualification surface before testing.
- `/audit` — independently prove or refute every applicable release invariant using deterministic repository/runtime evidence.

Do **not** use `/build` to repair a failing candidate in the same job. Do **not** use `/solve` to redesign the candidate. Do **not** mutate production content, UX behavior or audio assets to make a result pass.

If evidence is incomplete because upstream work is absent, return `HOLD`. If an invariant is violated, return `FAIL` with the smallest owner-directed remediation request. A repaired candidate must be re-entered as a fresh `/refresh -> /audit` execution.

`/research` is allowed only when necessary to establish an external verification fact required by an existing invariant; it must not expand scope or become a repair path. `/learn` is not required for qualification.

## Scope

Continuously qualify candidate V2 branches/integration snapshots against the contract.

Required checks include at minimum:

- `V1_CHANGED_FILES = 0` for `series/seville-discovery/**`;
- V2 scene graph integrity and ordering;
- required scene fields and source traceability;
- no broken route links/schema references;
- audio manifest completeness and deterministic scene mapping when J4 assets exist;
- French lock;
- player/resume semantics;
- offline behavior where supported by the current product;
- lock-screen/background playback where supported by the current product;
- V2 visit-mode minimal-text budget;
- V1 fallback reachability;
- non-V2 regression evidence for any shared-code changes.

## Independence

J5 may add tests, fixtures and qualification reports only when those artifacts are themselves qualification evidence and do not change candidate behavior. It must not change production content, UX behavior or audio assets to make a failing candidate pass. A failure is returned to the owning worker/coordination.

No human audio gate is part of qualification.

## Result model

Return one of:

- `PASS` — all currently applicable required checks pass;
- `HOLD` — candidate is structurally incomplete because upstream work is not yet present;
- `FAIL` — a required invariant is violated.

For every result include:

- candidate branch/ref and exact SHA;
- kernel path actually used;
- exact checks run and evidence;
- failing paths/scene IDs/invariants where applicable;
- proof that no repair mutation was performed;
- the smallest owner-directed remediation request.
