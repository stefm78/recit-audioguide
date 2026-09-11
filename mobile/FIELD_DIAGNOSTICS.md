# Android field diagnostics

The field build must never leave the visitor on an unexplained permanent `Chargement…` state.

The mobile series page embeds a bounded in-app event log (100 entries) and exposes `window.RECIT_DIAG` with stages, errors and a copyable JSON snapshot. The field monitor is injected before the series runtime and therefore remains useful even when `app.js` itself fails to load or execute.

Expected startup stages include:

1. Moniteur terrain actif
2. Données Séville embarquées
3. app.js exécuté
4. Lecture des données du guide
5. Données locales acceptées
6. Construction des épisodes
7. Interface construite
8. Guide prêt

A failure or an 8-second watchdog timeout reveals the diagnostic surface with current URL/origin, series slug, embedded-data presence, episode/playable counts, first audio URL and the latest runtime events. JavaScript errors, unhandled promise rejections, missing resources and audio errors are captured.

The Android visible application name is `00 Récit Séville Field`; the technical package remains `com.stefm78.recitaudioguide.field` so the stable field-test signing/update path is preserved.

`verify-runtime-browser.mjs` executes the packaged series page in a browser-like DOM, waits for the real ready marker, requires at least ten rendered episodes, clicks the first play control and proves the resulting audio URL resolves to a packaged local file.
