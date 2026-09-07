import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_v11_factory_contract_is_bounded_and_preserves_v1():
    contract = load("series/city-guide-factory-v1.1.json")
    assert contract["schema"] == "recit.city-guide-factory.v1_1"
    assert contract["version"] == "1.1"
    assert contract["invariants"]["accepted_route_is_immutable_without_material_defect"] is True
    assert contract["invariants"]["default_experience_remains_playable_without_optional_content"] is True
    assert contract["invariants"]["no_new_backend_required"] is True
    assert contract["content_model"]["optional_extensions"].startswith("Use existing episode.extras")
    assert contract["preproduction_brief"]["constraints"]["visitor_lenses_max"] == 3
    assert contract["content_model"]["cross_city_thread"].startswith("Optional narrative continuity")
    assert contract["navigation_model"]["embedded_routing"] == "OUT_OF_SCOPE_UNTIL_PROVEN_NECESSARY"
    assert contract["sound_model"]["automatic_soundscape"] is False


def test_bordeaux_artistic_gate_has_three_layered_architectures_and_preserves_route():
    gate = load("series/bordeaux-discovery/creative-brief-gate-v1.1.json")
    assert gate["status"] == "PENDING_HUMAN"
    assert gate["baseline"]["human_review"] == "PASS"
    assert gate["baseline"]["preserve"] is True
    assert gate["baseline"]["route_change_allowed"] is False
    assert [p["id"] for p in gate["proposals"]] == ["A", "B", "C"]
    assert all(p["narrative_spine"] == "city_transformation" for p in gate["proposals"])
    assert all(1 <= len(p["visitor_lenses"]) <= 3 for p in gate["proposals"])
    assert all(p["target_episode_minutes"] > 0 for p in gate["proposals"])
    assert gate["proposals"][0]["cross_city_thread"] == "optional_later"
    assert gate["proposals"][1]["cross_city_thread"] == "compatible"
    assert gate["proposals"][2]["cross_city_thread"] == "enabled_for_experiment"


def test_visit_overview_is_external_and_does_not_replace_step_navigation():
    series = load("series/bordeaux-discovery/series.json")
    overview = series["visit"]["overview_maps_url"]
    assert overview.startswith("https://www.google.com/maps/dir/")
    assert "waypoints=" in overview
    assert series["visit"]["routing_provider"] == "external_link_only"
    assert all(e["maps_url"].startswith("https://www.google.com/maps/") for e in series["episodes"])


def test_generic_frontend_exposes_route_overview_without_bordeaux_specific_code():
    js = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8")
    assert "overview_maps_url" in js
    assert "Voir le parcours complet" in js
    assert "dataRouteOverview" not in js  # property is created through dataset, not a city-specific selector
    assert "bordeaux" not in js.lower()
