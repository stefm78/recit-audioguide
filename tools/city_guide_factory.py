#!/usr/bin/env python3
"""Validate City Guide Factory v1 pre-audio route proposals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "recit.city-guide-factory.proposal.v1"
STATUS = "HUMAN_ROUTE_GATE"
BLOCKED = "BLOCKED_PENDING_HUMAN_ROUTE_GATE"
REQUIRED_DOWNSTREAM = (
    "scripts",
    "production_plan",
    "sound_direction",
    "audio_engine_render",
    "site_publication",
)


def _https(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if data.get("status") != STATUS:
        errors.append(f"status must be {STATUS}")

    request = data.get("request")
    if not isinstance(request, dict):
        errors.append("request must be an object")
    else:
        for key in ("city", "duration_budget", "mobility", "audience"):
            if not request.get(key):
                errors.append(f"request.{key} is required")

    evidence = data.get("evidence")
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty array")
    else:
        for item in evidence:
            if not isinstance(item, dict):
                errors.append("each evidence item must be an object")
                continue
            eid = item.get("id")
            if not eid or eid in evidence_ids:
                errors.append(f"evidence id missing or duplicated: {eid!r}")
            else:
                evidence_ids.add(eid)
            if not _https(str(item.get("url", ""))):
                errors.append(f"evidence {eid!r} must have an https URL")
            if not item.get("proves"):
                errors.append(f"evidence {eid!r} must state what it proves")

    route = data.get("route")
    stop_ids: set[str] = set()
    if not isinstance(route, list) or len(route) < 2:
        errors.append("route must contain at least two ordered stops")
    else:
        for index, stop in enumerate(route, start=1):
            if not isinstance(stop, dict):
                errors.append(f"route[{index}] must be an object")
                continue
            sid = stop.get("id")
            if not sid or sid in stop_ids:
                errors.append(f"route stop id missing or duplicated: {sid!r}")
            else:
                stop_ids.add(sid)
            for key in ("name", "address", "launch", "editorial_reason"):
                if not stop.get(key):
                    errors.append(f"route stop {sid!r}.{key} is required")
            refs = stop.get("evidence_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(f"route stop {sid!r} needs evidence_refs")
            else:
                unknown = [ref for ref in refs if ref not in evidence_ids]
                if unknown:
                    errors.append(f"route stop {sid!r} references unknown evidence: {unknown}")
            forbidden = [key for key in stop if "audio" in key.lower()]
            if forbidden:
                errors.append(f"pre-gate stop {sid!r} must not contain audio fields: {forbidden}")

    verification = data.get("route_verification")
    if not isinstance(verification, dict):
        errors.append("route_verification must be an object")
    else:
        if verification.get("gate_safe") is not True:
            errors.append("route_verification.gate_safe must be true")
        if not verification.get("method"):
            errors.append("route_verification.method is required")
        for key in ("exact_distance", "exact_walk_time"):
            value = verification.get(key)
            if value not in ("not_asserted", None):
                errors.append(f"{key} cannot be asserted by v1 without frozen routing evidence")

    downstream = data.get("downstream")
    if not isinstance(downstream, dict):
        errors.append("downstream must be an object")
    else:
        for key in REQUIRED_DOWNSTREAM:
            if downstream.get(key) != BLOCKED:
                errors.append(f"downstream.{key} must remain {BLOCKED}")

    gate = data.get("human_gate")
    if not isinstance(gate, dict) or not gate.get("question"):
        errors.append("human_gate.question is required")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proposal", type=Path)
    args = parser.parse_args()
    data = json.loads(args.proposal.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS: {args.proposal} is a valid {SCHEMA} pre-audio proposal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
