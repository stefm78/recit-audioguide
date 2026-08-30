# Historical branch closeout — 2026-08-30

Authority: GOV-WP-001 / issue #50.

This note records the durable disposition of the remaining historical branches in `stefm78/recit-audioguide` before deleting their refs.

No audio, Program, TTS provider, Audio Engine pin or open product candidate is changed by this closeout.

## Closed branches

| Branch | Exact historical HEAD | Durable authority | Disposition |
| --- | --- | --- | --- |
| `production-v1` | `0b9a5d6272115f816a230bc75c0683cc19e1b3eb` | PR #39, merged as `d4b9ce8cce3bfe673d41f61ef52f455fa07f2f07` | `MERGED_HISTORY_CAN_DELETE_REF` |
| `audit-production-states` | `ac412a3144acdfc3d1e31b178f1b4f2a28c16e0a` | PR #40, merged as `da348cc10de5411dfbcada2728e7efc777f19be3` | `MERGED_HISTORY_CAN_DELETE_REF` |
| `player-simple-controls-v1` | `3d302935ec5c7c2c94ac643bab711dd709bf4110` | PR #41, merged as `16a0ba9855d40d20cf278743a83c67a3139f23e2` | `MERGED_HISTORY_CAN_DELETE_REF` |
| `production-v1-final` | `0e176db5de315a1f61df68208950cbb91165328d` | parallel pre-PR candidate, audited below | `SUPERSEDED_CANDIDATE_CAN_DELETE_REF` |

## PR #39 — Production v1

PR #39 is the accepted caller-owned Production v1 sequence-orchestration implementation.

Its historical head was:

```text
production-v1
0b9a5d6272115f816a230bc75c0683cc19e1b3eb
```

It was merged on 2026-08-23 as:

```text
d4b9ce8cce3bfe673d41f61ef52f455fa07f2f07
```

The branch ref no longer carries independent authority.

## PR #40 — graceful production states

PR #40 materialized:

- episode states `ready|warning|failed`;
- series states `ready|degraded|blocked`;
- partial-production publication;
- stale-output removal after a failed program;
- explicit fallback preservation;
- UI behavior that avoids presenting an unusable Listen action.

Historical head:

```text
audit-production-states
ac412a3144acdfc3d1e31b178f1b4f2a28c16e0a
```

Merged authority:

```text
da348cc10de5411dfbcada2728e7efc777f19be3
```

The branch ref is redundant.

## PR #41 — practical player controls

PR #41 added the accepted compact player behavior:

- rewind 15 seconds;
- play/pause;
- forward 15 seconds;
- clickable progress;
- elapsed/total time;
- Media Session integration;
- corrected bonus progress persistence.

Historical head:

```text
player-simple-controls-v1
3d302935ec5c7c2c94ac643bab711dd709bf4110
```

Merged authority:

```text
16a0ba9855d40d20cf278743a83c67a3139f23e2
```

The branch ref is redundant.

## `production-v1-final` — superseded parallel candidate

This branch was never associated with a pull request.

Exact historical chain:

```text
c6c4bea03397fccf30a4b752fea10810b52a3b78
Add minimal sequence production orchestrator

0e176db5de315a1f61df68208950cbb91165328d
Configure Jeanne for derived scene-sequence production
```

Its two unique artifacts were audited.

### Jeanne production specification

Historical blob:

```text
701a25dd65e83fb5ae984f593fbfc8edc9ffbede
```

Current-main blob:

```text
701a25dd65e83fb5ae984f593fbfc8edc9ffbede
```

Therefore the production specification is byte-identical to current `main` and has no unique content to preserve.

### Alternate production orchestrator

Historical `tools/production.py` blob:

```text
d2cf758b795aee0f4526a464d7ada253ee5c277e
```

It was a 430-line alternate sequence implementation using derived sequence artifacts and production fingerprints.

The accepted implementation was instead promoted through PR #39 and subsequently hardened by PR #40. Current `tools/production.py` is different by design and is the repository authority.

The alternate candidate must not be resurrected merely because its branch exists. Its relevant product intent is already represented by:

- PR #39 history;
- PR #40 robustness behavior;
- current `tools/production.py`;
- the later Production Plan / long-form evidence proving that `scene-sequences` is optional and lossy for direct authored v6 soundscapes.

Disposition:

```text
production-v1-final
SUPERSEDED_CANDIDATE_CAN_DELETE_REF
```

## Active branch explicitly retained

The following ref must remain:

```text
feature/nuit-apres-orleans-prototype
203268827d5c5e7d7312545f465b653c5bd31690
```

It is the head of open PR #42, `Prototype immersif — La nuit après Orléans`.

Its remaining gate is human listening. This branch is **not historical debris** and must not be deleted, rebased, normalized through `scene-sequences`, or promoted without that gate.

## Final branch policy after cleanup

Expected durable refs:

```text
main
feature/nuit-apres-orleans-prototype
```

Any cleanup implementation must use exact-SHA guards and fail rather than delete a ref whose head moved.
