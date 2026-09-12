# IOS_NATIVE_FIELD_B30

Status: `PREPARED / PHYSICAL INSTALL BLOCKED BY APPLE SIGNING GATE`

## Frozen baseline

- Android FIELD B30: physical PASS.
- iPhone Safari/WebKit B30: physical PASS.
- Product baseline commit: `243d3556292258e137b3b709a0b9d3efbd7283e5`.
- Version: `0.4.30` / build `30`.
- Bundle ID: `com.stefm78.recitaudioguide.field`.
- Expected native display name: `00 Récit FIELD B30`.
- Frozen source release: `android-field-b30-frozen`.
- Frozen APK SHA-256: `857278af9c71b57933bf182900cf254d2ada150fed1c6c5d523c62dc8c9e0f48`.

No product behavior is reopened by this gate.

## What CI proves before any Apple credentials exist

`.github/workflows/ios-native-field-b30.yml`:

1. checks out the exact B30 commit independently of current `main`;
2. verifies the frozen B30 release and APK SHA-256;
3. rebuilds the B30 FIELD runtime with the B30 run/build identity forced to `30` / `243d3556`;
4. proves that the rebuilt `mobile/www` tree is byte-identical to the Web runtime physically present in the frozen B30 APK;
5. creates and syncs the Capacitor iOS shell;
6. applies native-only identity metadata (`00 Récit FIELD B30`, version `0.4.30`, build `30`);
7. compiles an unsigned archive for `generic/platform=iOS`;
8. verifies bundle ID, version/build, B30 identity and Library markers in the archived app;
9. publishes the unsigned `.xcarchive` as CI evidence.

The unsigned archive is **not installable on an iPhone**. It is intentionally not presented as a physical-test artifact.

## Physical-install decision

The user has an iPhone but no Mac.

There are only two first-party Apple paths relevant here:

- free Personal Team provisioning: requires Xcode connected to the personal device and expires periodically;
- remote distribution/TestFlight: requires Apple Developer Program distribution credentials.

Because there is no Mac available, the bounded native path selected for this project is:

`GitHub Actions macOS -> Apple automatic provisioning -> App Store Connect/TestFlight -> physical iPhone`.

No third-party signing service, shared certificate, enterprise-certificate workaround or profile bypass is authorized.

## One-time external gate for TestFlight

The signed `testflight` mode is fail-closed. It requires GitHub Actions secrets with these exact names:

- `APPLE_TEAM_ID`
- `APP_STORE_CONNECT_KEY_ID`
- `APP_STORE_CONNECT_ISSUER_ID`
- `APP_STORE_CONNECT_PRIVATE_KEY_BASE64`

The `.p8` private key must be base64-encoded before storage as a GitHub Actions secret. It must never be committed to the repository or pasted into logs/issues/PRs.

The Apple account must also have:

- active Apple Developer Program membership;
- an App Store Connect app record associated with bundle ID `com.stefm78.recitaudioguide.field`;
- a role/API key permitted to upload and manage the build.

Once those prerequisites exist, run workflow `iOS native FIELD B30 gate` with input `mode=testflight`.

The workflow uses the exact frozen B30 checkout, Apple automatic provisioning and App Store Connect key authentication. It then submits build `0.4.30 (30)` to TestFlight. Apple processing and assigning the build to a tester/group remain external Apple gates.

## Physical gate

Once B30 is installable from TestFlight, test only:

- `INSTALL_IDENTITY`: app installs and identifies as B30;
- `SAFE_AREA_HOME`: home and top navigation remain clear of iPhone system areas;
- `HOME_LIBRARY_NAV`: Library drawer, filters and local hide/show;
- `SERIES_NAVIGATION`: Séville plus one non-Séville route;
- `FIRST_AUDIO`: playback starts;
- `BACKGROUND_SCREEN_LOCK`: behavior in background and lock screen;
- `MEDIA_CONTROLS_INTERRUPTION`: observable native media controls/interruption behavior;
- `PERSISTENCE`: playback position and Library preference survive relaunch.

Stop at the first physical FAIL and diagnose only that failure. Do not reopen Android B30 or Safari B30 gates.

## Gate semantics

Until a signed build is physically installed and tested:

`IOS_NATIVE_FIELD_B30 = BLOCKED_EXTERNAL_APPLE_SIGNING_GATE`

A successful simulator build or unsigned device archive must never be upgraded to physical PASS.
