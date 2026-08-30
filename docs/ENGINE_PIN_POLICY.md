# Audio Engine pin policy

Récit audioguide pins Audio Engine by exact commit SHA.

## Current production pin

```text
3392d4f22f0a9b054a05b5c05a7856985c0ab030
```

This value is repeated where GitHub Actions syntax requires literal refs:

- reusable `hydrate-sounds.yml` workflow ref;
- reusable workflow `engine_ref` input;
- preview checkout of `stefm78/audio-engine`;
- production checkout of `stefm78/audio-engine`.

The cheap test `tests/test_engine_pin_coherence.py` requires all four to remain identical.

## Why the current pin is not bumped automatically

On 2026-08-30, the comparison from the consumer pin to Audio Engine
`294a1d84687199007dd7d542466ff39b2b4ac353` spans 73 commits.

The delta includes real runtime changes, including:

- `src/audio_engine/providers/edge.py`;
- `src/audio_engine/voice/render.py`;
- `src/audio_engine/voices.py`;
- `src/audio_engine/cli.py`;
- new preflight/runtime-support code.

Therefore a pin bump is not metadata maintenance. It can alter produced speech or assembly.

Current decision:

```text
AUDIO_ENGINE_PIN_PROMOTION = HOLD
CURRENT_CONSUMER_PIN = KEEP
```

## Promotion rule

A future pin promotion is a separate compatibility work package.

Order:

```text
cheap contract validation
    ->
representative consumer preview/full render
    ->
automatic timing/audio QA
    ->
compare against current consumer output
    ->
human listening only if perceptual output materially changes
    ->
promote exact pin
```

Never change only one of the four literal refs.

A pin upgrade must not be bundled with unrelated story, Sound Direction, UI, Voice Lab or TTS-model work.
