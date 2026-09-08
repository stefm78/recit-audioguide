import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "series" / "seville-discovery"


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_route_is_autonomously_accepted_from_dominant_candidate():
    proposal = load("proposal.json")
    accepted = load("accepted-route.json")
    assert proposal["candidate_comparison"]["verdict"] == "MATERIALLY_SUPERIOR_FOR_STATED_INTENT"
    assert proposal["candidate_comparison"]["human_gate_needed"] is False
    assert accepted["status"] == "ACCEPTED"
    assert accepted["decision"] == "ACCEPT_ROUTE"
    assert accepted["decision_source"] == "kernel_autonomous_A3"
    assert accepted["accepted_proposal_blob_sha"] == "9de329fa03420c173c5f756b143439221361da8c"
    assert accepted["route_order"] == [f"seville-cgf-0{i}" for i in range(1, 8)]


def test_visit_preserves_interview_constraints_and_generic_navigation():
    series = load("series.json")
    assert series["type"] == "visit"
    assert series["visit"]["transport_mode"] == "walking"
    assert series["visit"]["routing_provider"] == "external_link_only"
    assert series["visit"]["overview_maps_url"].startswith("https://www.google.com/maps/dir/")
    assert len(series["episodes"]) == 7
    assert "J-2/J-1" in series["note"]
    assert any("Casa Morales" in e["stop"] for e in series["episodes"])
    assert any("Real Alcázar" in e["stop"] for e in series["episodes"])
    for episode in series["episodes"]:
        assert len(episode.get("extras", [])) <= 3
        assert episode["maps_url"].startswith("https://www.google.com/maps/")
    for episode in series["episodes"][:-1]:
        assert episode["next_step"]["precision"] == "indicative"
        assert episode["next_step"]["walk_minutes"] <= 11


def test_two_level_editorial_model_is_base_plus_optional_gourmandises():
    series = load("series.json")
    assert all(e["summary"] for e in series["episodes"])
    assert sum(len(e.get("extras", [])) for e in series["episodes"]) >= 5
    assert any(len(e.get("extras", [])) == 0 for e in series["episodes"])
    titles = [x["title"] for e in series["episodes"] for x in e.get("extras", [])]
    assert all(title.startswith("Gourmandise") for title in titles)


def test_every_seville_audio_program_is_sourced_narrator_only_and_soundscape_free():
    for i in range(1, 8):
        program = load(f"audio/seville-discovery-ep0{i}.json")
        assert program["schema_version"] == 3
        assert program["profile"] == "speech"
        assert program["language"] == "fr-FR"
        assert program["sources"]
        assert len(program["segments"]) >= 3
        assert "soundscape" not in program
        assert all(segment["character_id"] == "narrateur" for segment in program["segments"])


def test_route_specific_logic_does_not_leak_into_generic_frontend():
    app = (ROOT / "web" / "app.js").read_text(encoding="utf-8").lower()
    next_step = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8").lower()
    assert "seville" not in app
    assert "sevilla" not in app
    assert "seville" not in next_step
    assert "sevilla" not in next_step
