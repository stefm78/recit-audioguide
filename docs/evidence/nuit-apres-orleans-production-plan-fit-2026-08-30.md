# Long-form Production Plan fit audit — La nuit après Orléans

Date: 2026-08-30

Authority: `recit-audioguide#43`, Pilot B.

Source under audit is read-only:

```text
PR #42
HEAD 203268827d5c5e7d7312545f465b653c5bd31690
Program blob   a966f1e6572d8ed7897181ce7c404d3cf10d6a34
Direction blob a51f7799bd5be6ac44913aa19ab0b1dae5f7470d
Series blob    6dff9bfe13ca77adc3370ba42aed73591d0bcecf
```

No file in PR #42 is modified by this audit.

## What the real prototype proves

The direct Audio Engine v6 Program contains:

- 150 segments;
- 9 narrative scenes;
- 6 speaking roles;
- 7 authored sound events;
- 13 Sound Direction beats.

Casting is not reducible to one static voice setting per character. Martin has 24 distinct voice/rate/pitch/volume combinations across his 50 segments and Agnès has 16 across 31 segments. Those variations are deliberate acting state, not configuration noise.

This is exactly the case where `program-ref` is safer than inline compilation: the Program remains the text and execution authority while the Production Plan records continuity, production priority, fallback and long-form context.

## Production Plan fit

The machine-readable companion proposes a Production Plan envelope with:

- `product = audiobook` for this long-form story use case;
- exact `program-ref` binding to the 150-segment Program;
- character continuity selectors by `character_id`;
- nine scene-range overlays;
- no spoken text;
- five existing human-risk hints carried forward from PR #42;
- Audiobook continuity/assembly context.

Detailed acoustic handoffs stay in the existing Sound Direction sidecar. They are not copied into Production Plan.

Verdict:

```text
LONGFORM_PLAN_FIT_AUDITED = PASS
PROGRAM_REF = CORRECT_BINDING
SOUND_DIRECTION = KEEP_SEPARATE
NO_COMMON_COMPILER_YET
```

## Why legacy scene-sequences is lossy

The current legacy strategy is intentionally simple. Its bridge generation fixes:

```text
foreground_ms          3200
carry_under_speech_ms  7000
gain_db                -16
fade_in_ms             120
fade_out_ms            1400
```

The real prototype does not follow those constants. Examples include:

| anchor | authored foreground | authored carry | tail | gain | fades |
| ---: | ---: | --- | ---: | ---: | --- |
| 65 | 1000 ms | 1 rendered segment | 0 ms | -31 dB | 180 / 650 ms |
| 66 | 2300 ms | 2 rendered segments | 900 ms | -29 dB | 450 / 1500 ms |
| 90 | 4200 ms | 2 rendered segments | 1200 ms | -27 dB | 700 / 1700 ms |
| 149 | 3000 ms | 1 rendered segment | 1200 ms | -29 dB | 650 / 1800 ms |

There are also three authored `scene` events that are not bridges.

More fundamentally, `scene-sequences` currently rejects a source Program that already has `soundscape` or `ambience`. Forcing this prototype through it would therefore require stripping the exact v6 soundscape first and recreating a poorer approximation.

Verdict:

```text
LEGACY_SEQUENCE_LOSS_DOCUMENTED = PASS
LEGACY_SCENE_SEQUENCES = DO_NOT_APPLY
```

## Human gate

This audit does **not** promote PR #42 and does not replace its listening gate.

The remaining human questions are unchanged:

- naturalness of adolescent voices;
- narrator/dialogue balance;
- bell → silence → river transition;
- spontaneous understanding of the halt before Meung;
- final river fade.

No new human request is introduced.
