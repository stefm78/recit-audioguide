# Visit Experience v1

Status: PRODUCT EXPERIMENT / backward-compatible

## Purpose

Turn a `visit` series from an itinerary with commentary into an on-site discovery experience. Navigation remains external and authoritative; the audioguide owns attention, observation, interpretation and optional depth.

The visitor loop is:

**see → understand → feel → continue**

## Grammar

An episode may expose a compact field program using these units:

- `ARRIVAL` — orient the visitor in 10–30 seconds without breaking immersion.
- `LOOK` — point to one concrete visible feature.
- `STORY` — give the minimum narrative needed to understand the place.
- `REVEAL` — introduce a fact or interpretation that materially changes what is being seen.
- `MOVE` — accompany a short movement.
- `SILENCE` — intentionally stop narration and let the place take attention.
- `COMPARE` — connect the current place with a previous or future stop.
- `HUMAN_STORY` — anchor an abstract process in people, work or lived experience.
- `OPTIONAL_DEPTH` — offer a non-required deep dive.
- `EXIT` — close the idea and prepare the next step.

Not every episode needs every unit. A unit exists only when it improves the field experience.

## Two levels

### Level 1 — Main visit

Short, fluid and immediately useful on site. Prefer one idea at a time and observable evidence over encyclopedic coverage.

### Level 2 — Gourmandises

Optional depth. A gourmandise must answer a real curiosity such as “why?”, “how do we know?”, “who actually did this?”, “what does this term mean?” or “what is the darker side of this history?”. It must never be required to understand the main visit.

## Field rules

1. Tell the visitor what to look at before explaining it when possible.
2. Use directions such as “turn around”, “look up”, “compare”, “walk to”, only when they are physically robust.
3. Prefer observable details: water channels, ramps, changes of scale, materials, axes, light, inscriptions, street width, sound transitions.
4. Silence is a valid editorial unit.
5. Navigation and narrative are separate: Google Maps / real conditions remain the route authority.
6. Do not use unverified legends as facts.
7. Sound direction may support attention, but sound must help the visitor see or feel rather than decorate narration.
8. Avoid cognitive overload while walking: move complex institutional or historiographical detail to optional depth.

## Mobile contract

For a visit series with `assets/visit-experience.json`, the Web surface may expose a compact **Maintenant** companion containing:

- current step;
- why it matters;
- what to look at first;
- estimated field duration;
- listen action;
- route action;
- optional depth;
- next step.

The visitor should understand **where am I / what do I do / what do I listen to** in under five seconds.

## Compatibility

`assets/visit-experience.json` is additive. A series without it keeps the existing UI and semantics unchanged.
