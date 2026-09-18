# J1 Sunday — build provenance reconciliation

Status: `FINAL_BASE_RECONCILED`

This file records the direct Git provenance for the Sunday J1 batch after the integration branch advanced during execution.

- First integration HEAD observed during `/refresh`: `3c5b0418f112616a40c62ec1ffe964d4a5b85ec2`.
- Integration HEAD observed at final mutation CAS: `dff97fabb6912e67f5b404bf1d617858c42ba6c9`.
- The latter is a strict descendant of the former; Git comparison showed it three commits ahead and zero behind.
- Accepted Sunday research candidate commit: `b0f56aff7ee996fcdeb5ca32a3f7b99eebacd1a4`.
- Direct parent of that candidate: `dff97fabb6912e67f5b404bf1d617858c42ba6c9`.
- Candidate delta from that parent: only `SUNDAY_FIELD_STORY_RESEARCH.md` and `SUNDAY_SOURCE_MANIFEST.md`.
- Earlier worker-side commits created while the J1 ref still exposed the stale pre-integration parent are superseded and are not part of the final branch history.
- No merge commit was created.

Interpretation rule for downstream workers: when `SUNDAY_FIELD_STORY_RESEARCH.md` or `SUNDAY_SOURCE_MANIFEST.md` mentions `3c5b0418…`, treat it as the first observed / intended integration baseline during the job, not the final Git parent. This provenance record plus the actual commit parent establish the final base as `dff97fab…`.
