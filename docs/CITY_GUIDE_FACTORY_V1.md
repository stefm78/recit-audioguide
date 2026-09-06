# City Guide Factory v1

Status: CANDIDATE — pre-audio human gate

## Goal

Turn a bounded visit request into a verified itinerary proposal that a human can accept before scripts, audio rendering, or publication are started.

The factory is a product-layer contract in `recit-audioguide`. It does not add TTS, mixing, voice casting, or audio packaging; those remain responsibilities of `stefm78/audio-engine`.

## Minimal flow

`visit request -> evidence -> candidate stops -> scored/ordered itinerary -> HUMAN_ROUTE_GATE -> scripts -> existing Production Plan/Sound Director -> audio-engine -> existing static site`

## Design constraints

- Reuse existing `visit` / `route` product semantics.
- A new city is content, not city-specific code.
- No permanent backend, database, or user account is required.
- The pre-gate artifact must contain no generated audio and must not pretend that estimates are routing-engine measurements.
- Factual claims used to select or explain a stop require sources.
- Ambiguous or unverified locations remain blocked rather than guessed.
- The human gate is a visual decision surface, not merely a JSON review.
- Every gate-ready stop needs map coordinates with provenance.
- Walking distance/time must be present with an explicit precision status. `ROUTED_FROZEN` means provider-backed evidence is frozen; `INDICATIVE_NOT_ROUTED` means the value is decision-support only and must disclose its method.

## Proposal contract

A proposal JSON contains:

- `schema`: `recit.city-guide-factory.proposal.v1`
- `status`: `HUMAN_ROUTE_GATE`
- `request`: city, duration budget, mobility and audience/preferences
- `review_summary`: visit budget, stop count, walking distance/time, effort, buffer, accessibility note and metric provenance/status
- `route`: ordered stops with stable IDs, names, verified addresses, map coordinates, launch context, editorial reason, evidence refs and per-leg metrics
- `evidence`: authoritative/primary URLs and what each source proves
- `route_verification`: method, result and explicit limits
- `downstream`: the exact post-acceptance steps; all remain blocked before human acceptance
- `human_gate`: concise decision, review surface and optional adjustments

## Human review surface

The static site exposes a generic route review page:

`reviews/route.html?slug=<proposal-slug>`

The page presents:

- a mobile-first map with numbered stops and itinerary order;
- total visit budget, stop count, walking distance/time and effort;
- a visible distinction between routed/frozen metrics and indicative estimates;
- each leg's approximate distance/time;
- the editorial reason and launch context for each stop;
- a decision area for `ACCEPT_ROUTE`, `ADJUST_ROUTE`, or `REJECT_ROUTE`.

The map polyline is intentionally only an order visualization unless routing evidence is `ROUTED_FROZEN`; it must not masquerade as turn-by-turn pedestrian guidance.

## Gate semantics

`HUMAN_ROUTE_GATE` is deliberately before script/audio production.

Accepting a route authorizes preparation of narrative scripts and normal product production artifacts for that route. It does not bypass the existing factual, audio, artistic or publication QA gates.

Rejecting or adjusting the route invalidates only the route-dependent stages; research evidence may be reused when still applicable.

## Vertical-slice acceptance criteria

City Guide Factory v1 reaches its first meaningful gate when:

1. a previously untreated city has a concrete ordered itinerary;
2. every selected stop has a verified real-world identity/address and map coordinates or is fail-closed;
3. the editorial selection is supported by attributable evidence;
4. route realism, walking time and distance are visible with honest precision/provenance semantics;
5. the proposal is rendered on the generic visual review surface;
6. no script/audio work has been spent before the route decision;
7. the artifact is sufficient to generate the existing `series.json`, scripts, Production Plan/Sound Director inputs and audio-engine jobs immediately after acceptance.
