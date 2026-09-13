# French native default — cross-project consumer qualification

**Status:** HUMAN_CROSS_PROJECT_LISTENING_GATE. Candidate only; no product pin, Pages or FIELD publication changed.

- Récit baseline: `de0f9cbe603c0dca4e1fc35fcf0e320b4639b00f`
- Current engine pin: `3392d4f22f0a9b054a05b5c05a7856985c0ab030`
- Candidate engine: `2fc024ee41984e2d9eaa454cf4edeeb3e63c741c`
- Old default narrator: `fr-FR-RemyMultilingualNeural`
- Candidate native French narrator: `fr-FR-HenriNeural`
- A/B source text is identical; only the engine/preset voice resolution changes.

## Listening order

- `seville-old.mp3` -> `seville-native-fr.mp3`: French continuity around Puerta del León / Patio de las Doncellas; natural Spanish proper-name pronunciation is allowed.
- `orleans-old.mp3` -> `orleans-native-fr.mp3`: Narrator timbre, rhythm and French naturalness; pay attention to Orléans, Charles VII, Reims and Jeanne.
- `kernel-handover-old.mp3` -> `kernel-handover-native-fr.mp3`: Modern/technical French, English loan words such as kernel/handover/City Guide, and overall intelligibility.

## Explicit-cast control

Odyssée P1 is inventoried as an explicit-cast control. Its explicit voices are not silently recast by this default policy.
Explicit multilingual French voices are listed in `inventory.json` as exceptions for any future stricter 'no multilingual French voice' policy.

See `provenance.json` for exact source sequences, text hashes, engine identities and audio hashes.
