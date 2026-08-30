#!/usr/bin/env python3
import argparse
import json


AUDIO_PREFIXES = (
    "series/",
)

AUDIO_EXACT = {
    "series/sound-direction-catalog.json",
    "tools/production.py",
    "tools/sound_direction.py",
}

SITE_PREFIXES = (
    "site/",
    "web/",
    "data/",
)


def classify(paths):
    paths = [str(path).replace("\\", "/").lstrip("./") for path in paths if str(path).strip()]
    audio_reasons = []
    build_reasons = []

    for path in paths:
        audio = False
        if path in AUDIO_EXACT:
            audio = True
        elif path.startswith("series/"):
            parts = path.split("/")
            if len(parts) >= 4 and parts[2] in {"audio", "direction"} and path.endswith(".json"):
                audio = True
            elif len(parts) == 3 and parts[2] in {"production.json", "sound-requirements.json"}:
                audio = True

        if audio:
            audio_reasons.append(path)

        build = audio
        if path.startswith(SITE_PREFIXES):
            build = True
        elif path.startswith("series/"):
            parts = path.split("/")
            if len(parts) == 3 and parts[2] == "series.json":
                build = True
            elif len(parts) >= 4 and parts[2] in {"episodes", "assets"}:
                build = True

        if build:
            build_reasons.append(path)

    return {
        "audio_needed": bool(audio_reasons),
        "build_needed": bool(build_reasons),
        "audio_reasons": sorted(set(audio_reasons)),
        "build_reasons": sorted(set(build_reasons)),
        "changed_count": len(paths),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Classify recit-audioguide changes by production cost")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--full", action="store_true", help="force audio and site production")
    args = parser.parse_args(argv)
    if args.full:
        result = {
            "audio_needed": True,
            "build_needed": True,
            "audio_reasons": ["workflow_dispatch"],
            "build_reasons": ["workflow_dispatch"],
            "changed_count": len(args.paths),
        }
    else:
        result = classify(args.paths)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
