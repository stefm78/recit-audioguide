# Mobile Offline MVP v1

## Goal

Turn the shared Capacitor shell into a field-testable offline product without forking the Récit product UI.

## Product invariant

`web/`, `series/` and the generated static `dist/` remain the shared product. Android and iOS must not contain guide-specific business logic.

## Offline package v1

The mobile build freezes one already-published production series into the shell. For the first qualification target this is `seville-discovery`.

The freezer:

1. starts from the deployed production `series.json`;
2. follows same-origin internal asset URLs recursively from the series object;
3. stores audio, transcripts, manifests and route data under the same relative paths used by the Web product;
4. writes `offline/<slug>/package-manifest.json` with byte counts and SHA-256 hashes;
5. fails if required narration assets cannot be fetched.

The verifier blocks the mobile build when an episode audio is absent, a referenced local asset is missing, or an HTML shell still auto-loads a remote script/stylesheet.

## Maps

The mobile payload deliberately removes the Leaflet CDN dependency. The existing textual route/leg UX remains available offline; external Google Maps links remain user-invoked online navigation aids. Offline map tiles are not claimed by this MVP.

## Qualified gates

- M1_SHARED_PRODUCT: the Web build is copied, not reimplemented.
- M2_PRODUCTION_FREEZE: the deployed production series is frozen locally.
- M3_INTEGRITY: package manifest carries SHA-256 for every fetched file.
- M4_CORE_OFFLINE: narration audio and referenced local route/transcript assets exist locally and HTML has no remote auto-loaded subresources.
- M5_ANDROID_COMPILE: debug APK compiles with the frozen payload.
- M6_IOS_COMPILE: unsigned simulator build compiles with the same payload.

## Gates intentionally left for a physical device

- D1 airplane-mode end-to-end visit;
- D2 screen-lock/background playback;
- D3 Bluetooth/headset media controls;
- D4 kill/restart/resume position;
- D5 interruption handling (call/audio focus);
- D6 storage pressure and package deletion/update.

Only after D1-D5 pass should native playback adapters be promoted from architectural option to required product capability.
