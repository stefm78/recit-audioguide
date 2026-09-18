# Séville V1 fallback baseline

Status: FROZEN_FALLBACK_REFERENCE

The existing `series/seville-discovery/**` experience is the operational fallback for Séville Field Guide V2.

Bootstrap source branch: `main`
Bootstrap source commit expected at coordination start: `de0f9cbe603c0dca4e1fc35fcf0e320b4639b00f`

Invariant for V2 worker changesets:

`git diff --name-only <V2_BASE>...<candidate> -- series/seville-discovery/` must be empty.

Workers must not treat this file as authority for current repository freshness. Before mutation they must revalidate their actual base/ref. The coordinating discussion owns current integration HEAD and resolves staleness.

V1 is not to be modernized, refactored or cleaned up as part of V2. A defect discovered in V1 is reported separately; it is not repaired inside a V2 job unless coordination explicitly opens a distinct V1 fix.
