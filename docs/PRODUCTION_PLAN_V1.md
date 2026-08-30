# Production Plan v1 in Récit audioguide

Récit audioguide is a consumer of the Production Plan v1 contract defined in `stefm78/audio-engine`.

Current contract authority:

```text
audio-engine main@294a1d84687199007dd7d542466ff39b2b4ac353
```

## Three different layers

Do not merge these concepts:

1. **Production Plan** — objective, continuity, production priorities, fallback/risk policy and product context.
2. **Sound Direction** — detailed artistic transfer of attention between voice, sound, silence and space.
3. **Production strategy** — optional implementation machinery such as legacy `scene-sequences`.

A Production Plan is not sent directly to the renderer.

## Existing content uses program-ref

Existing or long-form content uses `content_binding.mode = "program-ref"`.

The canonical Audio Engine Program remains the sole authority for spoken text and exact execution details. The plan:

- references the Program path;
- locks its exact Git blob SHA;
- contains no duplicated spoken text;
- attaches production overlays to one-based Program segment ranges;
- preserves existing Program soundscape/voice/timing decisions by default.

Any Program byte change breaks the cheap validation until the Production Plan is deliberately reviewed and rebound.

## Real pilot

The first real pilot is:

```text
series/orleans-cathedral/production-plan/orleans-cathedral-ep01.plan.json
```

It binds the existing Sainte-Croix episode 1 Program without modifying it.

Validation:

```bash
python tools/production_plan.py validate
```

This validation is offline, read-only and does not call Audio Engine, TTS or any network service.

## Long-form fit audit

The exact read-only audit of open PR #42, `La nuit après Orléans`, is preserved in:

- `docs/evidence/nuit-apres-orleans-production-plan-fit-2026-08-30.md`
- `docs/evidence/nuit-apres-orleans-production-plan-fit-2026-08-30.json`

It confirms that `program-ref` preserves a 150-segment direct v6 Program and its acting variation, while legacy `scene-sequences` would be lossy.

## Compiler decision

```text
NO_COMMON_COMPILER_YET
```

The current consumer needs validation and explicit intent preservation, not another orchestration layer.
