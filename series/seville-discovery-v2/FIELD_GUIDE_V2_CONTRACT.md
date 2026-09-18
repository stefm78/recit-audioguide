# Séville Field Guide V2 — Contract

Status: BOOTSTRAP
Scope: `series/seville-discovery-v2/**` plus V2-only presentation/runtime surfaces explicitly introduced for this series.

## Objective

Build a second, independent 3-day Seville experience that preserves the already-qualified V1 as an immediately usable fallback while raising the field experience to the qualitative benchmark observed during the 2026-09-17 live walk.

## Immutable fallback

- V1 authority/fallback surface: `series/seville-discovery/**`.
- V2 workers MUST NOT modify any path under `series/seville-discovery/**`.
- V2 MUST preserve the same trip invariants unless a separate coordination decision explicitly changes them: 3-day route intent, confirmed bookings, timing constraints, accommodation/logistics, luggage constraints and Google Maps as real navigation authority.
- V2 MUST expose an immediate path back to the V1 experience if the V2 field surface is unavailable or anomalous.
- `V1_CHANGED_FILES = 0` is a release invariant for all V2 changesets.

## Product principles

- `AUDIO_FIRST` — the guided visit is primarily listened to, not read.
- `FIELD_SCENE_IS_PRIMARY_UNIT` — episodes may remain production containers, but the lived runtime unit is a short field scene.
- `MINIMAL_ON_SCREEN_TEXT` — the normal visit surface shows only the current step, one short observation cue and essential controls.
- `LOOK_BEFORE_EXPLAIN` — when useful, the visitor observes or searches before receiving the reveal.
- `CITY_PRODUCES_THE_STORY` — use visible details, human stories, oddities, spatial contrasts and walking time rather than abstract exposition whenever possible.
- `SILENCE_IS_CONTENT` — intentional silence remains part of the guide.
- `OPTIONAL_DEPTH` — transcript, sources and deeper material remain available but are not in the primary flow.
- `NO_HUMAN_AUDIO_GATE` — audio production and publication do not require a human listening gate; human feedback may inform later revisions but is not a blocker.
- `AUTOMATED_QUALIFICATION` — technical and structural qualification is automated.

## Field grammar

Preferred scene grammar:

`PROMISE -> MOVE -> LOOK/SEARCH -> REVEAL -> HUMAN_STORY/CONTEXT -> CONNECT -> SILENCE/MOVE -> NEXT_PROMISE`

Not every scene needs every element. Avoid padding. The correct unit may be 20 seconds, 45 seconds, 90 seconds or several minutes depending on the place and the walking interval.

## Visit-mode UX target

The primary V2 visit surface should approximate:

- current step / total steps;
- short location or action label;
- one concise cue such as "Regardez d'abord...";
- prominent Play/Pause;
- essential actions: `Itinéraire`, `J'y suis`, `Continuer`;
- secondary actions behind an overflow or detail surface: `Je ne trouve pas`, `Approfondir`, `Transcription`, `Sources`, `Toutes les étapes`, `Version classique V1`.

Preparation/planning surfaces may remain information-rich. Visit mode must not behave like a document to read while walking.

## Worker boundaries

### J1 — FIELD STORY RESEARCH
May create/update only V2 research artifacts and source manifests. Must not change shared UX, V1, or final production audio.

### J2 — FIELD SHOWRUNNER
Consumes J1 research and writes V2 scene/program content. Must not change shared UX or V1.

### J3 — AUDIO-FIRST UX
May change V2-only presentation/runtime surfaces and, only when technically necessary, shared code guarded so non-V2 series behavior is unchanged. Must not change V1 Seville content or audio production.

### J4 — AUDIO PRODUCTION
Consumes J2-approved V2 scenes and produces V2 audio/manifests. Must not change route/logistics or V1.

### J5 — AUTOMATED QUALIFICATION
Verifies V1 immutability, V2 scene integrity, audio manifests, player behavior, resume/offline/screen-lock where supported, route links, minimal-text budget and V1 fallback reachability. It may add tests/qualification artifacts but must not repair production defects in the same job.

## Automated release invariants

At minimum:

- `V1_CHANGED_FILES = 0`
- `V2_SCENE_GRAPH = PASS`
- `V2_CONTENT_STRUCTURE = PASS`
- `V2_AUDIO_MANIFEST = PASS`
- `FRENCH_LOCK = PASS`
- `PLAYER = PASS`
- `RESUME = PASS`
- `OFFLINE = PASS` where the current product supports offline qualification
- `SCREEN_LOCK = PASS` where the current product supports background/lock-screen playback qualification
- `ROUTE_LINKS = PASS`
- `MINIMAL_TEXT_BUDGET = PASS`
- `V1_FALLBACK_REACHABLE = PASS`

No human audio gate is part of the release condition.

## Coordination model

This branch is a worker integration branch. Parallel worker discussions operate from explicit handovers/jobs. The coordinating discussion owns integration order, current HEAD knowledge, cross-stream conflicts and final merge decisions. Workers must return durable Git evidence: branch/ref, commit SHA, changed paths, tests/qualification and any blocker.

## Initial execution order

1. Bootstrap/freeze contract (this file).
2. Launch J1 Research and J3 Audio-First UX in parallel.
3. Start J2 progressively as J1 produces bounded route sections.
4. Start J4 progressively from J2 scene batches.
5. Run J5 continuously and independently.

No route, reservation or logistics redesign is part of this V2 unless coordination explicitly reopens it.
