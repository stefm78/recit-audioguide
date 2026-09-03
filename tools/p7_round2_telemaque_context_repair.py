#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

try:
    from tools import p7_round2_render as r2
except ModuleNotFoundError:
    import p7_round2_render as r2

ROOT = r2.ROOT
CONTRACT = r2.CONTRACT
MANIFEST = r2.MANIFEST
ENGINE_REF = "ae03c9afc641459ef9287dc528e127d357cbc615"
ROUND2_RELEASE_TAG = "odyssee-p7-round2-line-microprosody-v1"
ROUND2_FATHER_ASSET = "p7-r2-father-c.mp3"
ROUND2_FATHER_SHA256 = "cb72b83a5df08f4a8af958e0ddd6fc6b3af797253d08013a20c0101d6cd8484d"
REPAIR_RELEASE_TAG = "odyssee-p7-r2-father-context-repair-v1"
REPAIR_AUDIO = "p7-r2-father-context-repair.mp3"
REPAIR_QA = "p7-r2-father-context-repair.qa-report.json"
REPAIR_INDEX = "p7-r2-father-context-repair-index.json"
FATHER_ID = "father"
TELEMAQUE_SEGMENTS = (137, 139, 143, 145, 147, 149, 151, 153)
EXPECTED_TELEMAQUE_PRESET = {
    "voice": "fr-FR-RemyMultilingualNeural",
    "rate": "+5%",
    "pitch": "+8Hz",
    "volume": "+2%",
    "provider": "edge",
}


class RepairError(ValueError):
    pass


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_json(value):
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def father_window(contract):
    if contract.get("status") != r2.EXPECTED_STATUS:
        raise RepairError("Round 2 authority status drift")
    matches = [
        item for item in contract.get("windows") or []
        if item.get("id") == FATHER_ID
    ]
    if len(matches) != 1:
        raise RepairError("expected exactly one father Round 2 window")
    return matches[0]


def _preset_map(voice_pack):
    return r2.base._preset_map(voice_pack)


def _absolute_segments(program, start):
    return {
        start + offset: segment
        for offset, segment in enumerate(program.get("segments") or [])
    }


def _ulysse_snapshot(program, voice_pack, window):
    presets = _preset_map(voice_pack)
    ulysse = presets["odyssee-ulysse"]
    start = int(window["range"]["start_segment"])
    by_abs = _absolute_segments(program, start)
    result = []
    for number in window["ulysse_segments"]:
        segment = by_abs[number]
        override = window["C"]["segment_overrides"][str(number)]
        expected = {
            "segment": number,
            "speaker": "ULYSSE",
            "text": next(
                guard["text"]
                for guard in window["exact_guards"]
                if guard["segment"] == number
            ),
            "preset": "odyssee-ulysse",
            "voice": "fr-FR-HenriNeural",
            "provider": "edge",
            "rate": override["rate"],
            "pitch": override["pitch"],
            "volume": override["volume"],
            "pause_after_ms": int(override["pause_after_ms"]),
            "language_locale": "fr-FR",
        }
        observed = {
            "segment": number,
            "speaker": segment.get("speaker"),
            "text": segment.get("text"),
            "preset": segment.get("preset"),
            "voice": ulysse.get("voice"),
            "provider": ulysse.get("provider", "edge"),
            "rate": segment.get("rate"),
            "pitch": segment.get("pitch"),
            "volume": segment.get("volume"),
            "pause_after_ms": segment.get("pause_after_ms"),
            "language_locale": segment.get("language_locale"),
        }
        if observed != expected:
            raise RepairError(
                f"Ulysse Round 2 setting drift at segment {number}: "
                f"{observed!r} != {expected!r}"
            )
        result.append(observed)
    return result


def _telemaque_snapshot(program, voice_pack, window):
    presets = _preset_map(voice_pack)
    telemaque = presets.get("odyssee-telemaque")
    if not telemaque:
        raise RepairError("Télémaque preset missing")
    observed_preset = {
        key: telemaque.get(key)
        for key in ("voice", "rate", "pitch", "volume", "provider")
    }
    if observed_preset != EXPECTED_TELEMAQUE_PRESET:
        raise RepairError(
            f"Télémaque preset drift: {observed_preset!r}"
        )

    start = int(window["range"]["start_segment"])
    by_abs = _absolute_segments(program, start)
    guards = {
        int(item["segment"]): item
        for item in window["exact_guards"]
    }
    result = []
    actual_numbers = tuple(
        number
        for number in range(start, int(window["range"]["end_segment"]) + 1)
        if guards[number]["speaker"] == "TÉLÉMAQUE"
    )
    if actual_numbers != TELEMAQUE_SEGMENTS:
        raise RepairError("Télémaque exact segment scope drift")

    for number in TELEMAQUE_SEGMENTS:
        segment = by_abs[number]
        guard = guards[number]
        for key in ("speaker", "text", "preset"):
            if segment.get(key) != guard.get(key):
                raise RepairError(
                    f"Télémaque frozen {key} drift at segment {number}"
                )
        for forbidden in ("rate", "pitch", "volume"):
            if forbidden in segment:
                raise RepairError(
                    f"Télémaque artistic override forbidden at segment {number}"
                )
        if segment.get("language_locale") != "fr-FR":
            raise RepairError(
                f"Télémaque segment {number} must carry fr-FR transport locale"
            )
        result.append({
            "segment": number,
            "speaker": segment["speaker"],
            "text": segment["text"],
            "preset": segment["preset"],
            **observed_preset,
            "language_locale": "fr-FR",
        })
    return result


def materialize(out_dir, root=ROOT):
    root = Path(root).resolve()
    contract = load_json(CONTRACT)
    manifest = load_json(MANIFEST)
    window = father_window(contract)
    validated = r2.validate_window(window, root, manifest)
    program, voice_pack = r2.build_candidate(window, validated)

    program["id"] = "odyssee-p7-r2-father-context-repair"
    program["title"] = "P7 Round 2 father technical context repair"

    if len(program.get("segments") or []) != 19:
        raise RepairError("father repair must contain exactly S12 136-154")

    ulysse = _ulysse_snapshot(program, voice_pack, window)
    telemaque = _telemaque_snapshot(program, voice_pack, window)

    out_dir = Path(out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    program_path = out_dir / "father-context-repair.json"
    voices_path = out_dir / "father-context-repair.voices.json"
    write_json(program_path, program)
    write_json(voices_path, voice_pack)

    plan = {
        "schema": "recit.odyssee.p7_round2_telemaque_context_repair_plan.v1",
        "status": "READY_TO_RENDER_P7_R2_FATHER_CONTEXT_REPAIR",
        "engine_ref": ENGINE_REF,
        "authority_contract": str(CONTRACT.relative_to(root)),
        "authority_contract_sha256": sha256_file(CONTRACT),
        "source_program": window["source_program"],
        "source_program_git_blob_sha1": window["source_program_git_blob_sha1"],
        "range": copy.deepcopy(window["range"]),
        "program_id": program["id"],
        "program_path": str(program_path.relative_to(root)),
        "voice_pack_path": str(voices_path.relative_to(root)),
        "production_voice_pack": validated["voice_pack_path"],
        "production_voice_pack_sha256": validated["voice_pack_sha256"],
        "source_round2_release_tag": ROUND2_RELEASE_TAG,
        "source_round2_father_asset": ROUND2_FATHER_ASSET,
        "source_round2_father_sha256": ROUND2_FATHER_SHA256,
        "ulysse_round2_snapshot": ulysse,
        "ulysse_round2_snapshot_sha256": digest_json(ulysse),
        "telemaque_snapshot": telemaque,
        "telemaque_snapshot_sha256": digest_json(telemaque),
        "repair": {
            "scope": "TELEMAQUE_CONTEXT_LANGUAGE_TRANSPORT_ONLY",
            "spoken_language": "fr-FR",
            "transport_method": "FROZEN_FATHER_CONTEXT_CACHE_PRIME",
            "context_source": "EXACT_S12_136_154_FROZEN_TEXT_ONLY",
            "added_spoken_words": 0,
            "custom_ssml": False,
            "multilingual_voice_only": True,
            "ulysse_artistic_parameter_change": False,
            "recasting": False,
            "frozen_text_change": False,
            "provider_change": False,
            "production_program_mutation": False,
            "new_edge_tuning": False,
            "round3_edge": False,
        },
    }
    write_json(out_dir / "plan.json", plan)
    return plan


def _assert_transcript(plan, transcript):
    segments = transcript.get("segments") or []
    if len(segments) != 19:
        raise RepairError("repair transcript must contain exactly 19 segments")

    start = int(plan["range"]["start_segment"])
    by_abs = {
        start + offset: segment
        for offset, segment in enumerate(segments)
    }

    for expected in plan["ulysse_round2_snapshot"]:
        actual = by_abs[expected["segment"]]
        observed = {
            "segment": expected["segment"],
            "speaker": actual.get("speaker"),
            "text": actual.get("text"),
            "preset": actual.get("preset"),
            "voice": actual.get("voice"),
            "provider": actual.get("provider"),
            "rate": actual.get("rate"),
            "pitch": actual.get("pitch"),
            "volume": actual.get("volume"),
            "pause_after_ms": actual.get("pause_after_ms"),
            "language_locale": actual.get("language_locale"),
        }
        if observed != expected:
            raise RepairError(
                f"rendered Ulysse drift at {expected['segment']}"
            )

    for expected in plan["telemaque_snapshot"]:
        actual = by_abs[expected["segment"]]
        observed = {
            "segment": expected["segment"],
            "speaker": actual.get("speaker"),
            "text": actual.get("text"),
            "preset": actual.get("preset"),
            "voice": actual.get("voice"),
            "rate": actual.get("rate"),
            "pitch": actual.get("pitch"),
            "volume": actual.get("volume"),
            "provider": actual.get("provider"),
            "language_locale": actual.get("language_locale"),
        }
        if observed != expected:
            raise RepairError(
                f"rendered Télémaque transport drift at {expected['segment']}"
            )



def _context_text_and_spans(program, start_segment):
    texts = [str(item["text"]) for item in program.get("segments") or []]
    context = "\n".join(texts)
    spans = []
    cursor = 0
    for offset, text in enumerate(texts):
        spans.append({
            "segment": int(start_segment) + offset,
            "start": cursor,
            "end": cursor + len(text),
            "text": text,
        })
        cursor += len(text) + 1
    return context, spans


def _assign_word_boundaries(context, spans, events):
    assigned = {item["segment"]: [] for item in spans}
    cursor = 0
    for event_index, event in enumerate(events):
        token = str(event.get("text") or "")
        if not token:
            raise RepairError("Edge WordBoundary without text")
        found = context.find(token, cursor)
        if found < 0:
            raise RepairError(
                f"cannot map Edge WordBoundary token {token!r} after character {cursor}"
            )
        owner = next(
            (
                item
                for item in spans
                if item["start"] <= found < item["end"]
            ),
            None,
        )
        if owner is None:
            raise RepairError(
                f"Edge WordBoundary token {token!r} mapped outside a frozen line"
            )
        normalized = {
            "event_index": event_index,
            "text": token,
            "offset": int(event["offset"]),
            "duration": int(event["duration"]),
            "source_char": found,
        }
        assigned[owner["segment"]].append(normalized)
        cursor = found + len(token)
    return assigned


def _clip_bounds(events, first_index, last_index):
    first = events[first_index]
    last = events[last_index]
    first_start = int(first["offset"])
    last_end = int(last["offset"]) + int(last["duration"])

    start = first_start
    if first_index > 0:
        previous = events[first_index - 1]
        previous_end = int(previous["offset"]) + int(previous["duration"])
        if previous_end < first_start:
            start = previous_end + (first_start - previous_end) // 2

    end = last_end
    if last_index + 1 < len(events):
        following = events[last_index + 1]
        following_start = int(following["offset"])
        if last_end < following_start:
            end = last_end + (following_start - last_end) // 2

    if end <= start:
        raise RepairError("invalid frozen-context audio cut bounds")
    return start, end


def prime_context_cache(plan_path, cache_root, evidence_path):
    import asyncio
    import edge_tts

    from audio_engine.audio import run_ffmpeg
    from audio_engine.providers.edge import EdgeProvider
    from audio_engine.voice.render import (
        _materialize_provider_audio,
        voice_fingerprint,
    )
    from audio_engine.voices import resolve_segments

    plan = load_json(plan_path)
    if plan.get("status") != "READY_TO_RENDER_P7_R2_FATHER_CONTEXT_REPAIR":
        raise RepairError("repair plan is not ready for cache priming")
    if plan.get("engine_ref") != ENGINE_REF:
        raise RepairError("repair plan engine ref drift")

    program_path = ROOT / plan["program_path"]
    voices_path = ROOT / plan["voice_pack_path"]
    program = load_json(program_path)
    voices = load_json(voices_path)
    resolved = resolve_segments(program, voices)
    start_segment = int(plan["range"]["start_segment"])
    end_segment = int(plan["range"]["end_segment"])
    if end_segment - start_segment + 1 != len(resolved):
        raise RepairError("father context resolution length drift")

    context, spans = _context_text_and_spans(program, start_segment)
    expected_context = "\n".join(
        item["text"]
        for item in father_window(load_json(CONTRACT))["exact_guards"]
    )
    if context != expected_context:
        raise RepairError("context prime is not exact frozen S12 136-154 text")

    telemaque = []
    for number in TELEMAQUE_SEGMENTS:
        segment = resolved[number - start_segment]
        observed = {
            key: segment.get(key)
            for key in (
                "speaker",
                "text",
                "preset",
                "voice",
                "rate",
                "pitch",
                "volume",
                "provider",
                "language_locale",
            )
        }
        expected = next(
            item
            for item in plan["telemaque_snapshot"]
            if item["segment"] == number
        )
        expected_observed = {
            key: expected.get(key)
            for key in observed
        }
        if observed != expected_observed:
            raise RepairError(
                f"Télémaque resolved synthesis drift at segment {number}"
            )
        telemaque.append((number, segment))

    provider = EdgeProvider()
    context_audio = Path(cache_root).resolve().parent / "telemaque-frozen-context.raw.mp3"
    context_audio.parent.mkdir(parents=True, exist_ok=True)
    context_audio.unlink(missing_ok=True)
    word_events = []

    async def synthesize_context():
        communicator = edge_tts.Communicate(
            context,
            EXPECTED_TELEMAQUE_PRESET["voice"],
            rate=EXPECTED_TELEMAQUE_PRESET["rate"],
            pitch=EXPECTED_TELEMAQUE_PRESET["pitch"],
            volume=EXPECTED_TELEMAQUE_PRESET["volume"],
            boundary="WordBoundary",
        )
        communicator._audio_engine_language_locale = "fr-FR"
        communicator.tts_config._audio_engine_language_locale = "fr-FR"
        with context_audio.open("wb") as handle:
            async for message in communicator.stream():
                if message["type"] == "audio":
                    handle.write(message["data"])
                elif message["type"] == "WordBoundary":
                    word_events.append({
                        "text": message["text"],
                        "offset": int(message["offset"]),
                        "duration": int(message["duration"]),
                    })

    asyncio.run(synthesize_context())
    if not context_audio.is_file() or context_audio.stat().st_size <= 0:
        raise RepairError("frozen father context synthesis produced no audio")
    if not word_events:
        raise RepairError("frozen father context synthesis produced no WordBoundary evidence")

    assigned = _assign_word_boundaries(context, spans, word_events)
    cache_root = Path(cache_root).resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    unique = {}
    entries = []

    try:
        for number, segment in telemaque:
            boundaries = assigned.get(number) or []
            if not boundaries:
                raise RepairError(
                    f"no WordBoundary evidence for Télémaque segment {number}"
                )
            fingerprint = voice_fingerprint(segment, provider)
            if fingerprint in unique:
                prior = unique[fingerprint]
                entries.append({
                    "segment": number,
                    "fingerprint": fingerprint,
                    "cache_file": prior["cache_file"],
                    "cache_sha256": prior["cache_sha256"],
                    "alias_of_segment": prior["segment"],
                    "context_cut_reused": True,
                })
                continue

            first_index = boundaries[0]["event_index"]
            last_index = boundaries[-1]["event_index"]
            start_ticks, end_ticks = _clip_bounds(
                word_events,
                first_index,
                last_index,
            )
            raw_clip = cache_root / f"{fingerprint}.context-cut.tmp.mp3"
            final_clip = cache_root / f"{fingerprint}.mp3"
            if final_clip.exists():
                raise RepairError(
                    f"refusing to overwrite pre-existing Télémaque cache clip {fingerprint}"
                )
            run_ffmpeg([
                "-ss",
                f"{start_ticks / 10_000_000:.7f}",
                "-to",
                f"{end_ticks / 10_000_000:.7f}",
                "-i",
                str(context_audio),
                "-map_metadata",
                "-1",
                "-ac",
                "1",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "96k",
                str(raw_clip),
            ])
            _materialize_provider_audio(raw_clip, final_clip, provider)
            raw_clip.unlink(missing_ok=True)
            entry = {
                "segment": number,
                "fingerprint": fingerprint,
                "cache_file": str(final_clip),
                "cache_sha256": sha256_file(final_clip),
                "alias_of_segment": None,
                "context_cut_reused": False,
                "first_word": boundaries[0]["text"],
                "last_word": boundaries[-1]["text"],
                "start_ticks": start_ticks,
                "end_ticks": end_ticks,
            }
            unique[fingerprint] = entry
            entries.append(entry)
    finally:
        context_audio.unlink(missing_ok=True)

    if tuple(item["segment"] for item in entries) != TELEMAQUE_SEGMENTS:
        raise RepairError("context cache prime did not cover exact Télémaque scope")

    evidence = {
        "schema": "recit.odyssee.p7_r2_telemaque_frozen_context_prime.v1",
        "status": "TELEMAQUE_FROZEN_FATHER_CONTEXT_CACHE_READY",
        "engine_ref": ENGINE_REF,
        "context_source": "EXACT_S12_136_154_FROZEN_TEXT_ONLY",
        "context_sha256": hashlib.sha256(context.encode("utf-8")).hexdigest(),
        "context_segment_count": len(spans),
        "context_added_spoken_words": 0,
        "custom_ssml": False,
        "voice": EXPECTED_TELEMAQUE_PRESET["voice"],
        "rate": EXPECTED_TELEMAQUE_PRESET["rate"],
        "pitch": EXPECTED_TELEMAQUE_PRESET["pitch"],
        "volume": EXPECTED_TELEMAQUE_PRESET["volume"],
        "provider": EXPECTED_TELEMAQUE_PRESET["provider"],
        "root_language_locale": "fr-FR",
        "word_boundary_count": len(word_events),
        "telemaque_segment_count": len(entries),
        "unique_cache_clip_count": len(unique),
        "entries": entries,
        "ulysse_audio_synthesized_in_context_prime": False,
        "ulysse_round2_parameters_changed": False,
        "recasting": False,
        "frozen_text_change": False,
        "provider_change": False,
        "new_edge_tuning": False,
        "round3_edge": False,
    }
    write_json(evidence_path, evidence)
    return evidence


def collect(plan_path, render_root, release_out, product_sha, context_evidence_path):
    plan = load_json(plan_path)
    if plan.get("status") != "READY_TO_RENDER_P7_R2_FATHER_CONTEXT_REPAIR":
        raise RepairError("repair plan is not ready")
    if plan.get("engine_ref") != ENGINE_REF:
        raise RepairError("repair engine ref drift")
    repair = plan.get("repair") or {}
    forbidden_true = (
        "ulysse_artistic_parameter_change",
        "recasting",
        "frozen_text_change",
        "provider_change",
        "production_program_mutation",
        "new_edge_tuning",
        "round3_edge",
    )
    if any(repair.get(key) is not False for key in forbidden_true):
        raise RepairError("repair scope expanded beyond technical context")

    context_evidence = load_json(context_evidence_path)
    if context_evidence.get("status") != "TELEMAQUE_FROZEN_FATHER_CONTEXT_CACHE_READY":
        raise RepairError("Télémaque frozen-context cache evidence is not ready")
    if context_evidence.get("engine_ref") != ENGINE_REF:
        raise RepairError("Télémaque context evidence engine ref drift")
    if context_evidence.get("context_source") != "EXACT_S12_136_154_FROZEN_TEXT_ONLY":
        raise RepairError("Télémaque context source expanded beyond frozen father")
    if context_evidence.get("context_added_spoken_words") != 0:
        raise RepairError("Télémaque context prime added spoken words")
    if context_evidence.get("custom_ssml") is not False:
        raise RepairError("custom SSML is forbidden by Edge transport")

    render_dir = Path(render_root).resolve() / plan["program_id"]
    audio = render_dir / "audio.mp3"
    qa = render_dir / "qa-report.json"
    manifest = render_dir / "manifest.json"
    transcript_path = render_dir / "transcript.json"
    if not all(path.is_file() for path in (audio, qa, manifest, transcript_path)):
        raise RepairError("incomplete father context repair render")

    qa_data = load_json(qa)
    if qa_data.get("status") != "PASS":
        raise RepairError("father context repair machine QA failed")

    transcript = load_json(transcript_path)
    _assert_transcript(plan, transcript)
    manifest_data = load_json(manifest)
    fingerprints = (manifest_data.get("mix") or {}).get("voice_fingerprints") or []
    if len(fingerprints) != 19:
        raise RepairError("father repair manifest fingerprint count drift")
    expected_prime = {
        int(item["segment"]): item["fingerprint"]
        for item in context_evidence.get("entries") or []
    }
    for number in TELEMAQUE_SEGMENTS:
        if fingerprints[number - int(plan["range"]["start_segment"])] != expected_prime.get(number):
            raise RepairError(
                f"Télémaque segment {number} did not consume frozen-context cache"
            )
    if int((manifest_data.get("mix") or {}).get("voice_cache_hits") or 0) < len(TELEMAQUE_SEGMENTS):
        raise RepairError("father repair did not reuse all eight primed Télémaque cache slots")

    release_out = Path(release_out).resolve()
    if release_out.exists():
        shutil.rmtree(release_out)
    release_out.mkdir(parents=True, exist_ok=True)

    audio_target = release_out / REPAIR_AUDIO
    qa_target = release_out / REPAIR_QA
    shutil.copy2(audio, audio_target)
    shutil.copy2(qa, qa_target)

    index = {
        "schema": "recit.odyssee.p7_round2_telemaque_context_repair_index.v1",
        "status": "machine-ready-p7-r2-father-context-repair",
        "render_product_sha": product_sha,
        "engine_ref": ENGINE_REF,
        "authority_contract": plan["authority_contract"],
        "authority_contract_sha256": plan["authority_contract_sha256"],
        "source_program": plan["source_program"],
        "source_program_git_blob_sha1": plan["source_program_git_blob_sha1"],
        "range": plan["range"],
        "source_round2": {
            "release_tag": plan["source_round2_release_tag"],
            "father_asset": plan["source_round2_father_asset"],
            "father_sha256": plan["source_round2_father_sha256"],
        },
        "repair_audio": REPAIR_AUDIO,
        "repair_audio_sha256": sha256_file(audio_target),
        "qa": REPAIR_QA,
        "qa_sha256": sha256_file(qa_target),
        "qa_status": "PASS",
        "render_manifest_sha256": sha256_file(manifest),
        "transcript_sha256": sha256_file(transcript_path),
        "ulysse_round2_snapshot_sha256": plan["ulysse_round2_snapshot_sha256"],
        "telemaque_snapshot_sha256": plan["telemaque_snapshot_sha256"],
        "telemaque_segments": list(TELEMAQUE_SEGMENTS),
        "telemaque_voice": EXPECTED_TELEMAQUE_PRESET["voice"],
        "telemaque_spoken_language": "fr-FR",
        "telemaque_transport": "FROZEN_FATHER_CONTEXT_CACHE_PRIME",
        "context_prime_evidence_sha256": sha256_file(context_evidence_path),
        "context_prime": {
            "context_source": context_evidence["context_source"],
            "context_sha256": context_evidence["context_sha256"],
            "context_added_spoken_words": 0,
            "custom_ssml": False,
            "word_boundary_count": context_evidence["word_boundary_count"],
            "unique_cache_clip_count": context_evidence["unique_cache_clip_count"],
        },
        "ulysse_artistic_parameter_change": False,
        "recasting": False,
        "frozen_text_change": False,
        "provider_change": False,
        "production_program_mutation": False,
        "new_edge_tuning": False,
        "round3_edge": False,
        "frozen_round2_artistic_fail_evidence_preserved": True,
        "human_confirmation_scope": "FATHER_CONTEXT_TECHNICAL_INTEGRITY_ONLY",
    }
    write_json(release_out / REPAIR_INDEX, index)
    return index


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="P7 Round 2 father Télémaque technical context repair"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("materialize")
    prep.add_argument("--out", required=True)
    prime_cmd = sub.add_parser("prime-context-cache")
    prime_cmd.add_argument("--plan", required=True)
    prime_cmd.add_argument("--cache-root", required=True)
    prime_cmd.add_argument("--evidence", required=True)
    collect_cmd = sub.add_parser("collect")
    collect_cmd.add_argument("--plan", required=True)
    collect_cmd.add_argument("--render-root", required=True)
    collect_cmd.add_argument("--release-out", required=True)
    collect_cmd.add_argument("--product-sha", required=True)
    collect_cmd.add_argument("--context-evidence", required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "materialize":
            result = materialize(args.out)
        elif args.command == "prime-context-cache":
            result = prime_context_cache(
                args.plan,
                args.cache_root,
                args.evidence,
            )
        else:
            result = collect(
                args.plan,
                args.render_root,
                args.release_out,
                args.product_sha,
                args.context_evidence,
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (
        RepairError,
        r2.P7Round2Error,
        r2.base.P7RenderError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
