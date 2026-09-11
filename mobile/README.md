# Récit audioguide — shared mobile shell spike

This directory proves a narrow architectural question: can the existing static Web product be reused unchanged inside one Android/iOS shell while preserving the Web/PC surface?

## Scope

The spike deliberately keeps all product semantics in the existing Web/content layers. Native code is allowed only for capabilities that materially require the operating system, such as background media, file downloads/storage, lifecycle integration and store packaging.

The current spike first proves **same Web payload -> Android/iOS native containers**. It does not yet claim production-grade native background audio or downloadable guide packages; those are the next gates after the shell compiles and runs.

## Build input

1. Run the existing static build from the repository root:

```bash
python site/build.py
```

2. Prepare the exact same static payload for Capacitor:

```bash
cd mobile
npm install
npm run prepare:web
```

3. Generate a native platform locally when needed:

```bash
npx cap add android
npx cap sync android
```

or:

```bash
npx cap add ios
npx cap sync ios
```

`mobile/www/` and generated native platform directories are build artifacts and must not become a second source of product truth.

## Architectural boundary

Shared/product-owned:
- content schemas and `series/`;
- UI and visit experience in `web/`;
- `MAINTENANT`, extras/gourmandises, USER_PAUSE semantics, routing data;
- progress model and accessibility behavior;
- audio URLs/manifests as product data.

Platform adapters only:
- native playback/session lifecycle when required;
- downloads and filesystem;
- OS permissions;
- deep links, notifications if later justified;
- Android/iOS store packaging.

A native adapter must not know what a Giralda, Maestranza, gourmandise or visit day is.

## Non-goals of V1 spike

- no account system;
- no GPS autoplay;
- no native rewrite of the shared UI;
- no duplicated Android/iOS product logic;
- no App Store/Play production release;
- no replacement of the existing Web/PC deployment.
