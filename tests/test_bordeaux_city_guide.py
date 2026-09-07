import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES_DIR = ROOT / "series" / "bordeaux-discovery"


def load(name):
    return json.loads((SERIES_DIR / name).read_text(encoding="utf-8"))


def test_route_acceptance_is_exact_and_human():
    acceptance = load("route-acceptance.json")
    assert acceptance["decision"] == "ACCEPT_ROUTE"
    assert acceptance["authority"] == "human"
    assert acceptance["proposal"]["main_commit"] == "dfe66e3f6baa56820066bf0ae958a20231faadfb"
    assert len(acceptance["accepted_stop_ids"]) == 5


def test_fact_check_is_pass_for_scripting_and_route_precision_stays_held():
    fact_check = load("fact-check.json")
    assert fact_check["status"] == "PASS_FOR_SCRIPTING"
    held = [c for c in fact_check["claims"] if c["status"] == "HELD_OUT_OF_NARRATION"]
    assert any("distance" in c["claim"].lower() for c in held)


def test_series_is_generic_visit_with_next_step_navigation():
    series = load("series.json")
    assert series["type"] == "visit"
    assert series["visit"]["transport_mode"] == "walking"
    assert series["visit"]["routing_provider"] == "external-link-only"
    assert len(series["episodes"]) == 5
    for episode in series["episodes"][:-1]:
        nav = episode["next_navigation"]
        assert nav["mode"] == "walking"
        assert nav["url"].startswith("https://")
        assert nav["precision"] == "INDICATIVE_NOT_ROUTED"


def test_audio_programs_match_series_and_remain_narration_only():
    series = load("series.json")
    for index, episode in enumerate(series["episodes"], start=1):
        program = load(f"audio/bordeaux-discovery-ep0{index}.json")
        assert program["id"] == episode["id"]
        assert program["segments"]
        assert program["soundscape"]["events"] == []
        assert all(seg["character_id"] == "narrateur" for seg in program["segments"])


def test_web_surface_renders_provider_neutral_next_navigation():
    app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
    assert "function nextNavigation(e)" in app
    assert "e.next_navigation" in app
    assert "Étape suivante" in app
    assert "ROUTED_FROZEN" in app
