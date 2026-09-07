import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_v11_factory_contract_preserves_v1_and_free_form_control():
    contract = load("series/city-guide-factory-v1.1.json")
    assert contract["schema"] == "recit.city-guide-factory.v1_1"
    assert contract["version"] == "1.1"
    assert contract["invariants"]["accepted_route_is_immutable_without_material_defect"] is True
    assert contract["invariants"]["default_experience_remains_playable_without_optional_content"] is True
    assert contract["invariants"]["visitor_choice_is_explicit_not_algorithmically_forced"] is True
    assert contract["invariants"]["suggestions_are_open_ended_not_a_closed_taxonomy"] is True
    assert contract["creative_discovery"]["input_mode"] == "free_form_first"
    policy = contract["creative_discovery"]["suggestion_policy"]
    assert policy["closed_vocabulary_forbidden"] is True
    assert policy["persistent_persona_required"] is False
    assert policy["visitor_free_text_always_available"] is True
    assert policy["max_visible_suggestions_default"] <= 3
    assert contract["content_resolution"]["no_lock_in"].startswith("A selected suggestion")
    assert contract["navigation_model"]["embedded_routing"] == "OUT_OF_SCOPE_UNTIL_PROVEN_NECESSARY"
    assert contract["sound_model"]["automatic_soundscape"] is False


def test_bordeaux_gate_records_adjust_and_interactive_discovery():
    gate = load("series/bordeaux-discovery/creative-brief-gate-v1.1.json")
    assert gate["status"] == "ADJUST_ACCEPTED"
    assert gate["baseline"]["human_review"] == "PASS"
    assert gate["baseline"]["preserve"] is True
    assert gate["baseline"]["route_change_allowed"] is False
    assert "predefined thematic axes" in gate["human_direction"]
    experiment = gate["experiment"]
    assert "own words" in experiment["entry"]
    assert "never categories" in experiment["suggestion_behavior"]
    assert "ignore suggestions" in experiment["freedom"]
    assert "already-qualified" in experiment["reuse"]
    assert gate["next_gate"] == "PROVE_INTERACTIVE_DISCOVERY_WITH_ONE_BORDEAUX_STOP"


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
    assert "dataRouteOverview" not in js
    assert "bordeaux" not in js.lower()
