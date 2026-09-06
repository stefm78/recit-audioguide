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
- Exact walking distance/duration may only be asserted when backed by a routing provider or measured evidence. A geographically ordered route may still reach the human gate when stop identities and addresses are verified and the distance is explicitly marked `not_asserted`.

## Proposal contract

A proposal JSON contains:

- `schema`: `recit.city-guide-factory.proposal.v1`
- `status`: `HUMAN_ROUTE_GATE`
- `request`: city, duration budget, mobility and audience/preferences
- `route`: ordered stops with stable IDs, names, verified addresses, launch context, editorial reason and evidence refs
- `evidence`: authoritative/primary URLs and what each source proves
- `route_verification`: method, result and explicit limits
- `downstream`: the exact post-acceptance steps; all remain blocked before human acceptance
- `human_gate`: one concise decision and optional adjustments

## Gate semantics

`HUMAN_ROUTE_GATE` is deliberately before script/audio production.

Accepting a route authorizes preparation of narrative scripts and normal product production artifacts for that route. It does not bypass the existing factual, audio, artistic or publication QA gates.

Rejecting or adjusting the route invalidates only the route-dependent stages; research evidence may be reused when still applicable.

## Vertical-slice acceptance criteria

City Guide Factory v1 reaches its first meaningful gate when:

1. a previously untreated city has a concrete ordered itinerary;
2. every selected stop has a verified real-world identity/address or is fail-closed;
3. the editorial selection is supported by attributable evidence;
4. route realism has been checked without fabricating precision;
5. no script/audio work has been spent before the route decision;
6. the artifact is sufficient to generate the existing `series.json`, scripts, Production Plan/Sound Director inputs and audio-engine jobs immediately after acceptance.
