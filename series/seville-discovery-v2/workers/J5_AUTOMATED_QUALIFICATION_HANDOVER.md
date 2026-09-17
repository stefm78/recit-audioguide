# J5 — AUTOMATED QUALIFICATION — Worker Handover

## Mission

Independently prove or refute the Seville V2 release invariants. Do not repair defects in the same qualification job.

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

J5 may add tests, fixtures and qualification reports. It must not change production content, UX behavior or audio assets to make a failing candidate pass. A failure is returned to the owning worker/coordination.

No human audio gate is part of qualification.

## Result model

Return one of:

- `PASS` — all currently applicable required checks pass;
- `HOLD` — candidate is structurally incomplete because upstream work is not yet present;
- `FAIL` — a required invariant is violated.

For every result include candidate ref/SHA, exact checks run, evidence, failing paths/IDs, and the smallest owner-directed remediation request.
