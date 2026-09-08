import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "series" / "seville-discovery"


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def words(program):
    return sum(len((segment.get("text") or "").split()) for segment in program.get("segments", []))


def test_three_day_route_is_explicitly_human_approved_with_logistics_change():
    accepted = load("accepted-route.json")
    plan = load("final-plan.json")
    assert accepted["status"] == "ACCEPTED"
    assert accepted["decision"] == "ACCEPT_ROUTE"
    assert accepted["decision_source"] == "human_explicit_three_day_logistics_mission"
    assert plan["status"] == "HUMAN_TRAJECTORY_APPROVED"
    assert plan["dates"] == ["2026-09-18", "2026-09-19", "2026-09-20"]
    assert plan["route_change"] is True
    assert "NH Sevilla Plaza de Armas" in plan["hubs"]["day1"]
    assert plan["hubs"]["day2_day3"].startswith("Pje. de Vila, 11")


def test_visit_has_two_hubs_three_days_and_mixed_logistics():
    series = load("series.json")
    route_map = load("assets/route-map.json")
    assert series["visit"]["start"].startswith("NH Sevilla Plaza de Armas")
    assert len(series["visit"]["days"]) == 3
    assert len(series["episodes"]) == 10
    assert [e["day"] for e in series["episodes"]].count("day1") == 4
    assert [e["day"] for e in series["episodes"]].count("day2") == 4
    assert [e["day"] for e in series["episodes"]].count("day3") == 2
    assert route_map["secondary_hub"]["label"].startswith("NH Sevilla")
    modes = {leg.get("mode") for d in route_map["days"] for leg in d["legs"]}
    assert {"walking", "taxi", "pause", "luggage"}.issubset(modes)
    assert any(leg.get("audio_episode_id") == "seville-discovery-ep06" for leg in route_map["days"][0]["legs"])
    assert any(leg.get("audio_episode_id") == "seville-discovery-ep00" for leg in route_map["days"][1]["legs"])
    assert any(leg.get("audio_episode_id") == "seville-discovery-g02" for leg in route_map["days"][2]["legs"])
    assert any("Callejón del Agua" in leg["instructions"] for d in route_map["days"] for leg in d["legs"])
    assert any("bagages" in leg["instructions"].lower() for d in route_map["days"] for leg in d["legs"])
    assert any("18 h 30" in leg["instructions"] for leg in route_map["days"][2]["legs"])


def test_sunday_luggage_storage_is_resolved_without_inventing_operator_identity():
    series = load("series.json")
    plan = load("final-plan.json")
    route_map = load("assets/route-map.json")
    primary = plan["three_day_enrichment"]["sunday_luggage"]["primary"]
    fallback = plan["three_day_enrichment"]["sunday_luggage"]["adjacent_verified_fallback"]
    assert primary["address"].startswith("C. Agua, 7")
    assert primary["source"] == "human_supplied_existing_storage"
    assert primary["operator_public_identity"] == "TO_CONFIRM"
    assert fallback["address"].startswith("C. Agua, 5")
    assert fallback["sunday_hours"] == "11:00-19:00"
    assert "C. Agua, 7" in series["visit"]["luggage"]["sunday_primary"]
    assert "C. Agua 5" in series["visit"]["luggage"]["sunday_verified_backup"]
    day3 = route_map["days"][2]
    deposit = next(leg for leg in day3["legs"] if leg["mode"] == "luggage")
    airport = day3["legs"][-1]
    assert "C.%20Agua%2C%207" in deposit["maps_url"]
    assert "ne pas compter sur une prise en charge au pied" in airport["instructions"]
    assert "Paseo%20de%20Catalina%20de%20Ribera" in airport["maps_url"]


def test_main_programs_are_long_sourced_and_contextual():
    ids = ["ep06","ep07","ep04","ep02","ep00","ep05","ep01","ep03","g02","g13"]
    for suffix in ids:
        program = load(f"audio/seville-discovery-{suffix}.json")
        assert program["profile"] == "speech"
        assert program["language"] == "fr-FR"
        assert program["sources"]
        assert len(program["segments"]) >= 5
        assert words(program) >= 300
        assert "soundscape" not in program
        assert all(segment["character_id"] == "narrateur" for segment in program["segments"])


def test_perspectives_remain_real_optional_audio_programs_after_two_promotions():
    series = load("series.json")
    extras = [x for e in series["episodes"] for x in e.get("extras", [])]
    assert len(extras) >= 10
    assert all(x.get("id") for x in extras)
    assert all(len(e.get("extras", [])) <= 3 for e in series["episodes"])
    episode_ids = {e["id"] for e in series["episodes"]}
    assert "seville-discovery-g02" in episode_ids
    assert "seville-discovery-g13" in episode_ids
    for extra in extras:
        path = BASE / "audio" / f"{extra['id']}.json"
        assert path.exists(), extra["id"]
        program = json.loads(path.read_text(encoding="utf-8"))
        assert program["sources"]
        assert len(program["segments"]) >= 3
        assert "soundscape" not in program
        assert all(segment["character_id"] == "narrateur" for segment in program["segments"])


def test_generic_map_is_collapsible_and_supports_mixed_modes_without_seville_logic():
    visit_map = (ROOT / "web" / "visit-map.js").read_text(encoding="utf-8").lower()
    css = (ROOT / "web" / "styles.css").read_text(encoding="utf-8").lower()
    assert "visit-map-toggle" in visit_map
    assert "localstorage" in visit_map
    assert "max-width: 719px" in visit_map
    assert "taxi / vtc" in visit_map
    assert "bagages" in visit_map
    assert "dasharray" in visit_map
    assert ".visit-map-shell.collapsed" in css
    assert "seville" not in visit_map
    assert "sevilla" not in visit_map
