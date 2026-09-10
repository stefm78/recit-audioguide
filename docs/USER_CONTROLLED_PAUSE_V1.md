# User-Controlled Pause v1

## Decision

For field audioguides, contemplation time belongs to the visitor whenever the correct duration cannot be authored in advance.

Use a hybrid model:

- `MICRO_SILENCE`: short authored breathing space inside the audio; no user action.
- `USER_PAUSE`: the narrator explicitly hands control to the visitor, asks them to pause playback, gives a concrete observation task, and tells them to resume when they choose.

Do not use fixed long silence as a substitute for contemplation. Do not auto-pause the player by default.

## USER_PAUSE contract

A valid `USER_PAUSE` has four parts:

1. **Anchor** — the visitor is at a stable, safe place where stopping makes sense.
2. **Invitation** — natural spoken instruction to put the audio on pause.
3. **Freedom** — no countdown and no imposed duration; observation belongs to the visitor.
4. **Resume bridge** — the next spoken segment acknowledges the return and continues without assuming what the visitor noticed.

The instruction must be narratively integrated. Avoid repeatedly using the same formula.

## When to use

Use `USER_PAUSE` for a genuine change of attention regime: panorama, major spatial scale change, garden, courtyard, chosen artwork, or another moment where looking is the primary activity.

Do not use it for every detail, transition or short look prompt. Too many manual pauses create phone friction and damage immersion.

## Accessibility and robustness

The visitor remains in control of playback. The feature requires no timing metadata, no JavaScript synchronization with audio timecodes and no automatic playback mutation. Existing play/pause and persisted playback position remain the authority.

## UI

Render `USER_PAUSE` as `Pause libre · reprenez quand vous voulez`.

Render `MICRO_SILENCE` as `Respiration`.

This semantic distinction must remain visible even if an implementation later adds optional automatic pause support.
