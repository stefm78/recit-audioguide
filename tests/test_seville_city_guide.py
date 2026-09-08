import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "series" / "seville-discovery"


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def words(program):
    return sum(len((segment.get("text") or "").split()) for segment in program.get("segments", []))


def test_two_day_route_is_explicitly_human_approved_and_enriched_without_route_change():
    accepted = load("accepted-route.json")
    plan = load("final-plan.json")
    assert accepted["status"] == "ACCEPTED"
    assert accepted["decision"] == "ACCEPT_ROUTE"
    assert plan["status"] == "HUMAN_TRAJECTORY_APPROVED"
    assert plan["dates"] == ["2026-09-18", "2026-09-19"]
    assert plan["route_change"] is False
    assert plan["v1_1_enrichment"]["accepted_route_preserved"] is True


def test_visit_starts_at_hub_and_walks_are_content_bearing():
    series = load("series.json")
    route_map = load("assets/route-map.json")
    assert series["visit"]["start"].startswith("Pje. de Vila, 11")
    assert series["episodes"][0]["id"] == "seville-discovery-ep00"
    assert series["episodes"][0]["location"].startswith("Pje. de Vila")
    assert len(series["episodes"]) == 8
    assert [e["day"] for e in series["episodes"]].count("day1") == 5
    assert [e["day"] for e in series["episodes"]].count("day2") == 3
    assert any(leg.get("audio_episode_id") == "seville-discovery-ep00" for leg in route_map["days"][0]["legs"])
    assert any(leg.get("audio_episode_id") == "seville-discovery-ep06" for leg in route_map["days"][1]["legs"])
    assert any("Callejón del Agua" in leg["instructions"] for d in route_map["days"] for leg in d["legs"])
    assert all(leg["maps_url"].startswith("https://www.google.com/maps/dir/") for d in route_map["days"] for leg in d["legs"])


def test_main_programs_are_longer_sourced_and_pitch_gourmandises():
    ids = ["ep00","ep05","ep01","ep04","ep02","ep03","ep06","ep07"]
    for suffix in ids:
        program = load(f"audio/seville-discovery-{suffix}.json")
        assert program["profile"] == "speech"
        assert program["language"] == "fr-FR"
        assert program["sources"]
        assert len(program["segments"]) >= 5
        assert words(program) >= 300
        assert "soundscape" not in program
        assert all(segment["character_id"] == "narrateur" for segment in program["segments"])
        joined = " ".join(segment["text"].lower() for segment in program["segments"])
        assert "gourmandise" in joined or suffix in {"ep06"}


def test_perspectives_are_real_optional_audio_programs():
    series = load("series.json")
    extras = [x for e in series["episodes"] for x in e.get("extras", [])]
    assert len(extras) >= 10
    assert all(x.get("id") for x in extras)
    assert all(len(e.get("extras", [])) <= 3 for e in series["episodes"])
    for extra in extras:
        path = BASE / "audio" / f"{extra['id']}.json"
        assert path.exists(), extra["id"]
        program = json.loads(path.read_text(encoding="utf-8"))
        assert program["sources"]
        assert len(program["segments"]) >= 3
        assert "soundscape" not in program
        assert all(segment["character_id"] == "narrateur" for segment in program["segments"])


def test_generic_map_is_collapsible_without_seville_specific_logic():
    visit_map = (ROOT / "web" / "visit-map.js").read_text(encoding="utf-8").lower()
    css = (ROOT / "web" / "styles.css").read_text(encoding="utf-8").lower()
    assert "visit-map-toggle" in visit_map
    assert "localstorage" in visit_map
    assert "max-width: 719px" in visit_map
    assert ".visit-map-shell.collapsed" in css
    assert "seville" not in visit_map
    assert "sevilla" not in visit_map
