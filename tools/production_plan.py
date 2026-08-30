#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_PRODUCTS = {"audioguide", "audiobook"}
ALLOWED_IMPORTANCE = {"essential", "important", "supportive", "optional"}
ALLOWED_FALLBACK = {"fail", "omit-and-warn", "continue-without"}
ALLOWED_DISPOSITIONS = {"program", "consumer_metadata", "unsupported"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path):
    content = path.read_bytes()
    payload = b"blob " + str(len(content)).encode("ascii") + b"\0" + content
    return hashlib.sha1(payload).hexdigest()


def leaves(value, path=""):
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            result.update(leaves(item, f"{path}/{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.update(leaves(item, f"{path}/{index}"))
    else:
        result[path or "/"] = value
    return result


def pointer_get(value, pointer):
    current = value
    for part in pointer.strip("/").split("/"):
        if not part:
            continue
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current


def contains_key(value, wanted):
    if isinstance(value, dict):
        return wanted in value or any(contains_key(item, wanted) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, wanted) for item in value)
    return False


def resolve_program(plan_path: Path, plan):
    binding = plan.get("content_binding")
    if not isinstance(binding, dict) or binding.get("mode") != "program-ref":
        raise ValueError(f"{plan_path}: real pilot requires content_binding.mode=program-ref")
    if binding.get("content_authority") != "program":
        raise ValueError(f"{plan_path}: content_authority must be program")
    raw = binding.get("program")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"{plan_path}: content_binding.program is required")
    program_path = (ROOT / raw).resolve()
    if ROOT not in program_path.parents or not program_path.is_file():
        raise ValueError(f"{plan_path}: invalid Program path {raw}")
    expected = binding.get("git_blob_sha1")
    actual = git_blob_sha1(program_path)
    if expected != actual:
        raise ValueError(f"{plan_path}: Program blob drift: expected {expected}, got {actual}")
    return program_path, load(program_path), actual


def selector_matches(segment, selector):
    allowed = {"character_id", "preset", "speaker", "voice"}
    if not selector or not set(selector).issubset(allowed):
        return False
    return all(segment.get(key) == value for key, value in selector.items())


def validate_plan(plan_path: Path):
    plan = load(plan_path)
    if plan.get("production_plan_version") != 1:
        raise ValueError(f"{plan_path}: production_plan_version must be 1")
    if plan.get("product") not in ALLOWED_PRODUCTS:
        raise ValueError(f"{plan_path}: unsupported product")
    for key in ("id", "title", "language", "objective", "casting", "overlays", "fallback_policy", "risk_hints", "product_context"):
        if not plan.get(key):
            raise ValueError(f"{plan_path}: missing/non-empty {key}")
    if contains_key(plan, "text"):
        raise ValueError(f"{plan_path}: program-ref plan must not duplicate spoken text")

    program_path, program, blob_sha = resolve_program(plan_path, plan)
    for key in ("id", "title", "language"):
        if plan[key] != program.get(key):
            raise ValueError(f"{plan_path}: {key} differs from canonical Program")

    segments = program.get("segments") or []
    if not segments:
        raise ValueError(f"{plan_path}: canonical Program has no segments")

    for role, casting in plan["casting"].items():
        if not casting.get("continuity_key"):
            raise ValueError(f"{plan_path}: casting {role} missing continuity_key")
        selector = casting.get("program_selector")
        if not isinstance(selector, dict) or not any(selector_matches(s, selector) for s in segments):
            raise ValueError(f"{plan_path}: casting selector for {role} matches no Program segment")

    overlay_ids = set()
    for overlay in plan["overlays"]:
        overlay_id = overlay.get("id")
        if not overlay_id or overlay_id in overlay_ids:
            raise ValueError(f"{plan_path}: invalid/duplicate overlay id")
        overlay_ids.add(overlay_id)
        segment_range = overlay.get("segment_range")
        if (
            not isinstance(segment_range, list)
            or len(segment_range) != 2
            or not all(isinstance(v, int) for v in segment_range)
        ):
            raise ValueError(f"{plan_path}: overlay {overlay_id} has invalid segment_range")
        start, end = segment_range
        if start < 1 or end < start or end > len(segments):
            raise ValueError(f"{plan_path}: overlay {overlay_id} out of Program bounds")
        if overlay.get("importance") not in ALLOWED_IMPORTANCE:
            raise ValueError(f"{plan_path}: overlay {overlay_id} has invalid importance")
        if not overlay.get("performance_intent"):
            raise ValueError(f"{plan_path}: overlay {overlay_id} missing performance_intent")

    for key, value in plan["fallback_policy"].items():
        if value not in ALLOWED_FALLBACK:
            raise ValueError(f"{plan_path}: fallback {key} has invalid value")

    if plan["product"] == "audioguide":
        required = {
            "station_id", "location_label", "visual_cue", "target_duration_s",
            "max_duration_s", "resume_after_beats", "listening_environment",
            "next_step", "optional_content_policy",
        }
        if set(plan["product_context"]) != required:
            raise ValueError(f"{plan_path}: Audioguide product_context must contain exactly {sorted(required)}")
        if plan["product_context"]["target_duration_s"] > plan["product_context"]["max_duration_s"]:
            raise ValueError(f"{plan_path}: target duration exceeds maximum")
        unknown_resume = set(plan["product_context"]["resume_after_beats"]) - overlay_ids
        if unknown_resume:
            raise ValueError(f"{plan_path}: resume_after_beats references unknown overlays {sorted(unknown_resume)}")

    disposition_path = plan_path.with_name(plan_path.name.replace(".plan.json", ".disposition.json"))
    if not disposition_path.is_file():
        raise ValueError(f"{plan_path}: missing disposition companion")
    disposition = load(disposition_path)
    paths = [entry.get("path") for entry in disposition.get("entries", [])]
    if len(paths) != len(set(paths)):
        raise ValueError(f"{disposition_path}: duplicate disposition path")
    if set(paths) != set(leaves(plan)):
        missing = sorted(set(leaves(plan)) - set(paths))
        extra = sorted(set(paths) - set(leaves(plan)))
        raise ValueError(f"{disposition_path}: silent field loss; missing={missing}, extra={extra}")
    for entry in disposition["entries"]:
        kind = entry.get("disposition")
        if kind not in ALLOWED_DISPOSITIONS:
            raise ValueError(f"{disposition_path}: invalid disposition {kind}")
        if kind == "program":
            target = entry.get("target")
            if not target:
                raise ValueError(f"{disposition_path}: program disposition missing target")
            if target.startswith("/"):
                pointer_get(program, target)
            elif target.startswith("@program-selector:"):
                selector_key = target.split(":", 1)[1]
                value = leaves(plan)[entry["path"]]
                if not any(segment.get(selector_key) == value for segment in segments):
                    raise ValueError(f"{disposition_path}: selector target does not exist in Program")
            else:
                raise ValueError(f"{disposition_path}: unsupported program target {target}")
        else:
            if not entry.get("reason"):
                raise ValueError(f"{disposition_path}: non-program disposition missing reason")

    return {
        "id": plan["id"],
        "product": plan["product"],
        "mode": "program-ref",
        "program": str(program_path.relative_to(ROOT)),
        "program_git_blob_sha1": blob_sha,
        "segments": len(segments),
        "overlays": len(plan["overlays"]),
        "status": "valid",
    }


def validate_all():
    paths = sorted(ROOT.glob("series/*/production-plan/*.plan.json"))
    summaries = [validate_plan(path) for path in paths]
    result = {"status": "valid", "production_plans": len(summaries), "plans": summaries}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate consumer Production Plan v1 sidecars")
    parser.add_argument("command", choices=["validate"])
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            validate_all()
            return 0
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
