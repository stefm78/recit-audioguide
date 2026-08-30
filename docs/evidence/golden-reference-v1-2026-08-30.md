# Golden Reference v1 — La nuit après Orléans

Date: 2026-08-30  
Authority: issue #59 — GOLDEN-WP-001.

## Status

```text
GOLDEN_REFERENCE_V1 = FROZEN
HUMAN_ACCEPTED      = PASS
```

This reference is the first long-form perceptual non-regression authority for Récit audioguide.

## Perceptual authority

The human-accepted audio is the immutable review release:

```text
release:
pr42-human-review-v2

frozen candidate:
203268827d5c5e7d7312545f465b653c5bd31690

master SHA-256:
4fa33d168796ef745dc9bfae95ec58135490b673c048c998c8bda029d3674893

duration:
660.84 seconds
```

Human review:

```text
Naturel voix adolescentes        4/5
Équilibre narratrice/dialogues  4/5
Transition cloches-espace-eau   4/5
Compréhension halte avant Meung 4/5
Dernier fondu                   4/5
Défauts entendus                none
Decision                        PASS
```

## Promoted product authority

The accepted product content was promoted separately from the historical PR branch, preserving current-main CI and Audio Engine wiring.

At freeze:

```text
main:
016831abd7736c56ec5b6b79e54aedad3a305834

Program blob:
a966f1e6572d8ed7897181ce7c404d3cf10d6a34

Sound Direction blob:
a51f7799bd5be6ac44913aa19ab0b1dae5f7470d

Series blob:
6dff9bfe13ca77adc3370ba42aed73591d0bcecf
```

The promoted current-main rendering is a compatibility proof. It does not replace the human-accepted master as perceptual authority unless a later human review explicitly promotes a newer master.

## Regression rule

Do **not** compare MP3 bytes as the normal acceptance criterion.

A candidate engine/content change should first be checked mechanically for:

1. Program structure and segment count.
2. Character/casting identity.
3. Measured timing and duration bounds.
4. Sound-event count, order and semantic role.
5. Clipping/truncation.
6. Fades, tails and relative carry semantics.
7. Loudness/true-peak sanity.
8. Missing assets or speech segments.
9. Unexpected provider or voice changes.

A human re-listen is required only when these checks or the nature of the code change make a perceptually material difference plausible.

## What this freezes

This freeze protects the **quality bar and perceptual result**, not one implementation forever.

It therefore permits future Audio Engine improvements without forcing byte identity, but prevents a mechanically green change from silently lowering the quality accepted by the listener.

## Next narrative

The next long-form Production trial must use a **different story/theme**. It must not extend this Orléans story merely to avoid exercising new narrative and sound-design conditions.
