import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "series" / "bordeaux-discovery"


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_route_acceptance_is_frozen_to_reviewed_proposal():
    accepted = load("accepted-route.json")
    assert accepted["status"] == "ACCEPTED"
    assert accepted["decision"] == "ACCEPT_ROUTE"
    assert accepted["accepted_proposal_blob_sha"] == "c00ddcd4f6b706f3e354567481cee1f11a2c5e46"
    assert len(accepted["route_order"]) == 5


def test_visit_has_five_ordered_navigable_episodes():
    series = load("series.json")
    assert series["type"] == "visit"
    assert series["visit"]["transport_mode"] == "walking"
    assert len(series["episodes"]) == 5
    for episode in series["episodes"][:-1]:
        assert episode["maps_url"].startswith("https://www.google.com/maps/")
        assert episode["next_step"]["precision"] == "indicative"


def test_every_episode_program_has_sources_and_no_sound_design_dependency():
    for i in range(1, 6):
        program = load(f"audio/bordeaux-discovery-ep0{i}.json")
        assert program["schema_version"] == 3
        assert program["language"] == "fr-FR"
        assert len(program["sources"]) >= 2
        assert len(program["segments"]) >= 5
        assert program["soundscape"]["events"] == []
        assert all(segment["character_id"] == "narrateur" for segment in program["segments"])


def test_generic_next_step_asset_is_loaded():
    html = (ROOT / "web" / "series.html").read_text(encoding="utf-8")
    js = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8")
    build = (ROOT / "site" / "build.py").read_text(encoding="utf-8")
    assert "next-step.js" in html
    assert "Rejoindre l’étape suivante" in js
    assert "next-step.js" in build
