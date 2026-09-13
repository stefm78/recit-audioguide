# Audio Engine pin policy

Récit audioguide pins Audio Engine by exact commit SHA.

## Current production pin

```text
2fc024ee41984e2d9eaa454cf4edeeb3e63c741c
```

This pin corresponds to Audio Engine 0.9.4 and the qualified native French default policy:

- `fr-FR-HenriNeural` is the standard `fr-FR` narrator;
- `narrateur-vif` resolves to Henri with the existing `+8%`, `+14Hz`, `+5%` prosody;
- uncast `fr-FR` narration resolves through that language default;
- explicit voices, explicit role presets, existing character identities and non-empty casting targets remain authoritative and are not silently recast.

This value is repeated where GitHub Actions syntax requires literal refs:

- reusable `hydrate-sounds.yml` workflow ref;
- reusable workflow `engine_ref` input;
- preview checkout of `stefm78/audio-engine`;
- production checkout of `stefm78/audio-engine`.

The cheap test `tests/test_engine_pin_coherence.py` requires all four to remain identical.

## Promotion evidence for 0.9.4

The previous production pin was:

```text
3392d4f22f0a9b054a05b5c05a7856985c0ab030
```

The 0.9.4 promotion was qualified as a separate compatibility work package.

Evidence chain:

1. Audio Engine CI passed with regression coverage for the native `fr-FR` default and preservation of explicit casting.
2. A bounded Seville A/B probe isolated the multilingual code-switch defect and the native Henri candidate received human PASS.
3. Cross-project A/B qualification compared the exact previous pin to `2fc024ee41984e2d9eaa454cf4edeeb3e63c741c` on identical source text for Seville, Orléans and the Kernel handover technical narrative.
4. Human review accepted the native-French B variant for all three representative families.
5. Explicit Odyssée casting remained outside the default policy and was inventoried rather than silently recast.
6. Consumer CI must perform a complete audio qualification whenever `.github/workflows/pages.yml` changes, preventing an engine-pin promotion from taking the build-only path.

Promotion decision:

```text
AUDIO_ENGINE_PIN_PROMOTION = PASS
CURRENT_CONSUMER_PIN = 2fc024ee41984e2d9eaa454cf4edeeb3e63c741c
DEFAULT_FR_FR_NARRATOR = fr-FR-HenriNeural
```

## Promotion rule

A future pin promotion remains a separate compatibility work package.

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
human listening if perceptual output materially changes
    ->
complete consumer audio qualification
    ->
promote exact pin
```

Never change only one of the four literal runtime refs.

A pin upgrade must not be bundled with unrelated story, Sound Direction, UI, Voice Lab or TTS-model work.
