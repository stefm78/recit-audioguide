# MOBILE_SHARED_SHELL_SPIKE_V1

STATUS: CANDIDATE_SPIKE
PURPOSE: qualify one shared product across Web/PC, Android and iOS without a native rewrite.

## Decision under test

Candidate architecture:

```text
recit-audioguide content + web runtime
              |
        existing static build
              |
      ---------------------
      |         |         |
     Web     Android      iOS
  GitHub     Capacitor  Capacitor
   Pages       shell      shell
```

Web remains a first-class product surface. The mobile shell is additive.

## Evidence from current product

The repository already separates content (`series/`), Web UI (`web/`), static publishing (`site/`) and audio production (`audio-engine`). A new guide is intended to remain content, not a new application implementation.

The existing Web player already owns product-level playback UX, progress, seek and Media Session integration. The spike must reuse it unchanged first, then introduce a native playback adapter only if device testing proves the WebView media lifecycle insufficient.

## Gates

### G1 — SAME_PRODUCT_BUILD
PASS when the unmodified static `dist/` payload is copied into a Capacitor shell and both Android and iOS native projects can be generated from it.

### G2 — ANDROID_COMPILE
PASS when an Android debug APK compiles from the same payload in CI.

### G3 — IOS_COMPILE
PASS when the iOS project builds for an unsigned simulator target in CI from the same payload.

### G4 — DEVICE_OFFLINE
Human/device gate. With network disabled, a downloaded or bundled Séville payload must open and all required visit content/audio under test must remain usable.

### G5 — DEVICE_MEDIA_LIFECYCLE
Human/device gate. Required scenarios: screen lock, app background, headset/Bluetooth play/pause, interruption by phone/media, seek, USER_PAUSE, app restart and position resume.

### G6 — PACKAGE_INDEPENDENCE
PASS when a guide can be versioned/downloaded independently of the mobile application and validated by manifest/hash without shipping executable code.

## Package target

A future guide package should be data-only:

```text
<slug>/
  manifest.json
  series.json
  visit-experience.json (optional)
  assets/
  audio/
  routes/
  transcripts/
```

Minimum manifest fields:
- `schema`;
- `slug`;
- `version`;
- `minimum_app_version`;
- file list with size and SHA-256;
- total size;
- publication timestamp/source identity.

No downloaded package may introduce executable JavaScript/native code in the production model.

## Native boundary

Allowed native responsibilities:
- media playback/session adapter;
- download manager and filesystem;
- lifecycle/interruption handling;
- platform permissions;
- store packaging.

Forbidden native product duplication:
- visit grammar;
- guide-specific navigation semantics;
- gourmandises;
- USER_PAUSE meaning;
- episode/day business rules;
- guide-specific UI copies.

## Acceptance question

The architecture qualifies only if the answer remains YES to:

> Can one product change be implemented principally once and surface on Web/PC, Android and iOS with only bounded OS adapters?

If native platform code begins to own guide semantics or shared UI, the candidate must be re-challenged.
