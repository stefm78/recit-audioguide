import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "series" / "seville-discovery"


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_two_day_route_is_explicitly_human_approved():
    accepted = load("accepted-route.json")
    plan = load("final-plan.json")
    assert accepted["status"] == "ACCEPTED"
    assert accepted["decision"] == "ACCEPT_ROUTE"
    assert accepted["decision_source"] == "human_explicit_two_day_trajectory_approval"
    assert plan["status"] == "HUMAN_TRAJECTORY_APPROVED"
    assert plan["dates"] == ["2026-09-18", "2026-09-19"]
    assert len(accepted["route_order"]) == 7


def test_visit_uses_hub_two_days_and_editorial_walking_waypoints():
    series = load("series.json")
    route_map = json.loads((BASE / "assets" / "route-map.json").read_text(encoding="utf-8"))
    assert series["type"] == "visit"
    assert series["visit"]["transport_mode"] == "walking"
    assert series["visit"]["routing_provider"] == "external_google_maps_with_editorial_waypoints"
    assert series["visit"]["start"].startswith("Pje. de Vila, 11")
    assert len(series["visit"]["days"]) == 2
    assert len(route_map["days"]) == 2
    assert all(day["legs"] for day in route_map["days"])
    assert any("Callejón del Agua" in leg["instructions"] for day in route_map["days"] for leg in day["legs"])
    assert any("Paseo de Cristóbal Colón" in leg["instructions"] for day in route_map["days"] for leg in day["legs"])
    assert all(leg["maps_url"].startswith("https://www.google.com/maps/dir/") for day in route_map["days"] for leg in day["legs"])


def test_final_story_has_seven_playable_chapters_and_optional_perspectives():
    series = load("series.json")
    assert len(series["episodes"]) == 7
    assert [e["day"] for e in series["episodes"]].count("day1") == 4
    assert [e["day"] for e in series["episodes"]].count("day2") == 3
    assert any("Plaza de España" in e["stop"] for e in series["episodes"])
    assert any("Cathédrale" in e["stop"] for e in series["episodes"])
    assert any("Real Alcázar" in e["stop"] for e in series["episodes"])
    assert any("Triana" in e["stop"] for e in series["episodes"])
    assert sum(len(e.get("extras", [])) for e in series["episodes"]) >= 8
    assert all(len(e.get("extras", [])) <= 3 for e in series["episodes"])
    assert all(e.get("time") and e.get("day_label") for e in series["episodes"])


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


def test_generic_frontend_has_map_without_seville_specific_logic():
    app = (ROOT / "web" / "app.js").read_text(encoding="utf-8").lower()
    next_step = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8").lower()
    visit_map = (ROOT / "web" / "visit-map.js").read_text(encoding="utf-8").lower()
    html = (ROOT / "web" / "series.html").read_text(encoding="utf-8").lower()
    build = (ROOT / "site" / "build.py").read_text(encoding="utf-8").lower()
    for text in (app, next_step, visit_map):
        assert "seville" not in text
        assert "sevilla" not in text
    assert "visit-map.js" in html
    assert "visit-map.js" in build
    assert "leaflet" in html
