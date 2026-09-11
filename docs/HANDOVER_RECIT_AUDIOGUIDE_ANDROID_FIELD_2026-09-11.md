# HANDOVER — Récit audioguide / Android Field — 2026-09-11

STATUS: `KERNEL_HANDOVER_FORCED = COMPLETE`
CONTINUATION_READY: `YES`

This handover was explicitly forced by human authority. It is a continuity artefact, not a functional evolution.

## FACTS_VERIFIED

- Repository: `stefm78/recit-audioguide`.
- Product invariant: Web remains a first-class surface; Android/iOS are additive shared-shell targets. Product semantics stay in `web/` + `series/`; native code is reserved for OS capabilities.
- Before handover materialization, verified `main` product HEAD was `b1e2bb178366a2586f2bf8a4b914dc4a123a6c1e` (PR #210 merge).
- PR #210 `Mobile — hard reset field MVP with build identity` is merged.
- Main mobile workflow run `34637254247` / run number 17 completed SUCCESS on that product HEAD.
- Main Pages workflow run `34637254936` / run number 533 completed SUCCESS on that product HEAD.
- Release tag `android-field-latest` targets product HEAD `b1e2bb178366a2586f2bf8a4b914dc4a123a6c1e`.
- Current published field release is `Récit Séville — Android Field Test B17`, version `0.4.17`.
- Android package remains `com.stefm78.recitaudioguide.field`.
- Expected Android visible label for B17 is `00 Récit FIELD B17`.
- Expected in-app build identity is `FIELD BUILD 0.4.17 · b1e2bb17`.
- Published APK asset: `recit-seville-field.apk`.
- Published APK SHA-256: `c290d9939cf67ac88e8f78b3d38cc9158c9ed50198f4dca822441d353ed6b38e`.
- Release URL: `https://github.com/stefm78/recit-audioguide/releases/tag/android-field-latest`.
- Direct APK URL: `https://github.com/stefm78/recit-audioguide/releases/download/android-field-latest/recit-seville-field.apk`.
- The field mobile build embeds Séville offline and retains a runtime diagnostic monitor on the series page.
- The architecture documentation still defines physical-device gates for airplane mode, background/screen-lock media lifecycle, Bluetooth/headset controls, restart/resume and interruption handling.

## DECISIONS_FROZEN

1. Do not rewrite Récit as separate Android/iOS products.
2. Preserve the shared Web product as source of product semantics.
3. Keep Capacitor as the shared-shell candidate while field qualification continues.
4. Do not introduce native playback adapters until device evidence proves they are required.
5. For the current Android field milestone, reduce ambition aggressively: one statically exposed Séville launcher is sufficient to prove install/build identity and series navigation.
6. Real-device evidence outranks CI conclusions for usability.
7. No future Android field verdict is accepted until the installed build identity is visually confirmed first.
8. `FIELD_READY` is forbidden until a physical device confirms the series page renders and at least one real audio starts.

## CURRENT_STATE

The project has repeatedly produced CI-green Android APKs while the physical Samsung showed inconsistent/old-looking behavior. The last observed field evidence before PR #210 showed two distinct-looking home surfaces: one plain page stuck on `Chargement…`, and another styled page correctly showing the Séville card. This ambiguity made it impossible to know with confidence which APK/build was actually running.

PR #210 therefore introduced a hard-reset qualification mode:

- field home has a hard-wired static Séville launcher;
- no `home.js`, catalog fetch or JavaScript is required to expose the guide on the field home;
- every field home/series page carries exact build identity;
- Android app label is stamped per run (`00 Récit FIELD B<run>`);
- version is `0.4.<run>` with monotonic versionCode;
- installability verification checks package, version, app label and signer;
- series runtime keeps embedded data, diagnostics and browser execution gates.

Current best automated verdict:

`AUTOMATED_QUALIFICATION_PASS / INSTALL_IDENTITY_RETEST_REQUIRED`

No claim of `FIELD_READY` is valid yet.

## OPEN_PROBLEMS

1. The B17 APK has not yet been confirmed on the physical Samsung after this hard-reset change.
2. We do not yet know whether the device will visibly show `00 Récit FIELD B17` and `FIELD BUILD 0.4.17 · b1e2bb17`.
3. We do not yet know whether clicking the static Séville launcher on B17 reaches the series page correctly on the real device.
4. We do not yet have physical-device proof that a real local audio starts.
5. Airplane-mode end-to-end, screen-lock/background playback, Bluetooth/headset controls, kill/restart/resume and interruption handling remain unqualified human/device gates.

## FAILED_APPROACHES

The following approaches produced automated PASS but did not resolve the real-device problem and must not be repeated as sufficient evidence:

- PR #206: injected catalogue + series data and a fetch shim; CI proved navigation/audio paths but field behavior still remained problematic.
- PR #207: made series bootstrap consume embedded `RECIT_SERIES_DATA` directly and added a watchdog; still not enough on device.
- PR #208: fixed Pages deployments that could drop production audio assets on non-audio changes; necessary infrastructure fix, but not the real-device bootstrap proof.
- PR #209: added runtime monitor, bounded log, visible timeout diagnostics and jsdom browser execution; CI passed, but the next physical observation still showed that we could not trust build identity.
- Repeatedly rebuilding/republishing under the same human-visible identity without proving which build was installed created ambiguity and wasted cycles.

## DO_NOT_REPEAT

- Do not infer that a CI-green APK is the APK currently running on the phone.
- Do not debug the series page before confirming the exact build identity visible on-device.
- Do not add another fetch shim, timeout, loader or instrumentation layer merely because `Chargement…` appears.
- Do not increase product ambition until the minimal static launcher path works on the actual phone.
- Do not change package/signing identity casually; the stable field package/signature is intentional.
- Do not declare success from Web/browser/jsdom behavior alone.
- Do not obscure build identity again. Every field test build must remain unmistakable.

## NEXT_GATES

### GATE 0 — INSTALL_IDENTITY
Human gate, immediate priority.

Install/update from `android-field-latest`, then open the app. Required visible proof:

- launcher/app label: `00 Récit FIELD B17`;
- page banner: `FIELD BUILD 0.4.17 · b1e2bb17`.

Verdict:
- both match -> `BUILD_IDENTITY_CONFIRMED`;
- either differs -> `WRONG_BUILD_INSTALLED` and stop functional debugging.

### GATE 1 — STATIC_HOME_TO_SERIES
After identity confirmation only:

- Séville must be present without a loading phase;
- tap Séville;
- series page must render.

If it fails, capture the on-screen field diagnostic and exact visible build identity. Diagnose only that build.

### GATE 2 — FIRST_AUDIO
Once series page renders:

- choose first playable episode;
- tap `Écouter`;
- confirm audible playback from packaged local asset.

### GATE 3 — CORE_OFFLINE
Then test airplane mode end-to-end.

### GATE 4 — MEDIA_LIFECYCLE
Only after core offline playback passes: screen lock/background, Bluetooth/headset, interruption, restart/resume.

## USEFUL_REFERENCES

- `docs/MOBILE_SHARED_SHELL_SPIKE_V1.md`
- `docs/MOBILE_OFFLINE_MVP_V1.md`
- `mobile/FIELD_DIAGNOSTICS.md`
- `mobile/finalize-runtime.mjs`
- `.github/workflows/mobile-shared-shell-spike.yml`
- PR #206 — mobile bootstrap/navigation
- PR #207 — fetch-independent series runtime
- PR #208 — preserve production audio across non-audio deploys
- PR #209 — observable/executable field startup
- PR #210 — hard reset with build identity
- Release: `https://github.com/stefm78/recit-audioguide/releases/tag/android-field-latest`

## KERNEL / GOVERNANCE CONTINUITY

Kernel/control-plane state carried from the active project context (not independently stored or revalidated in this repository during this handover): Human authority -> UCP active -> UAO orchestrator active -> UAR `/research` -> UAS `/solve` -> UAB `/build` -> UAA `/audit` -> UAL `/learn`, with human gates and fail-closed mutation discipline. The handover itself is human-forced and therefore overrides any automatic handover threshold.

Applicable governance here:

- revalidate volatile GitHub state before any future mutation;
- human device evidence is an explicit gate;
- keep reversible/bounded changes until the gate passes;
- distinguish automated qualification from physical validation;
- do not mutate product state merely to continue the handover.

## FIRST_ACTION_IN_NEXT_CONVERSATION

Do not modify code first.

Ask for / inspect the physical Samsung result from B17 and classify it strictly as one of:

`BUILD_IDENTITY_CONFIRMED`

or

`WRONG_BUILD_INSTALLED`

If confirmed, proceed to `STATIC_HOME_TO_SERIES`; otherwise diagnose installation/update/cache/package state before touching application runtime.

## NEXT_CONVERSATION_BOOTSTRAP_PROMPT

`/audit /solve — Continue Récit audioguide Android Field from docs/HANDOVER_RECIT_AUDIOGUIDE_ANDROID_FIELD_2026-09-11.md as the continuity authority. Revalidate current main HEAD, PR/release/workflow state before any mutation. Do not repeat PR #206/#207/#209-style bootstrap fixes unless new evidence specifically proves they are relevant. The immediate human gate is INSTALL_IDENTITY for B17: the physical Android device must show app label "00 Récit FIELD B17" and on-screen banner "FIELD BUILD 0.4.17 · b1e2bb17". Classify the result first as BUILD_IDENTITY_CONFIRMED or WRONG_BUILD_INSTALLED. Only if identity is confirmed may you continue to STATIC_HOME_TO_SERIES, then FIRST_AUDIO. Treat device evidence as authority over CI. Keep the milestone deliberately minimal, fail closed, preserve Web/PC and iOS, and make no product mutation unless it directly addresses the first newly proven failing gate.`

## HANDOVER COMPLETENESS CHECK

- Où en sommes-nous ? -> automated B17 qualification complete; physical install identity not yet confirmed.
- Qu'est-ce qui fonctionne réellement ? -> Web/Pages CI, Android/iOS build CI, packaged offline assets, signing/installability metadata, release publication.
- Qu'est-ce qui ne fonctionne pas / reste non prouvé ? -> actual B17 install identity, series rendering on device, first audio on device, later lifecycle gates.
- Qu'a-t-on déjà essayé ? -> PR #206 through #210 sequence documented above.
- Que ne faut-il pas refaire ? -> CI-only bootstrap loops without first proving installed build identity.
- Prochain objectif ? -> confirm exact B17 on the phone.
- Prochain gate ? -> `INSTALL_IDENTITY`.
- Première action ? -> inspect the device-visible label/banner before any code change.

`KERNEL_HANDOVER_FORCED = COMPLETE`

`CONTINUATION_READY = YES`
