import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_v11_factory_anchors_discovery_in_every_module_creation():
    contract = load("series/city-guide-factory-v1.1.json")
    assert contract["schema"] == "recit.city-guide-factory.v1_1"
    assert contract["version"] == "1.1"
    assert contract["invariants"]["creative_discovery_is_part_of_every_module_creation"] is True
    assert contract["invariants"]["fixed_theme_catalog_not_required"] is True
    assert contract["invariants"]["requester_free_text_always_available"] is True
    assert contract["invariants"]["existing_qualified_guides_must_be_considered_for_reuse_or_connection"] is True

    lifecycle = contract["module_creation_lifecycle"]
    assert lifecycle["ordered_stages"][0] == "REQUEST_CAPTURE"
    assert lifecycle["ordered_stages"][1] == "CREATIVE_DISCOVERY"
    assert lifecycle["ordered_stages"][2] == "EXISTING_MATERIAL_RESOLUTION"
    assert lifecycle["ordered_stages"].index("MODULE_PROPOSAL") < lifecycle["ordered_stages"].index("RESEARCH_AND_FACT_CHECK")
    assert "not a Bordeaux-specific gate" in lifecycle["rule"]


def test_creation_discovery_is_free_form_suggestive_and_non_ontological():
    contract = load("series/city-guide-factory-v1.1.json")
    discovery = contract["creation_discovery"]
    assert discovery["input_mode"] == "free_form_first"
    assert "change direction during discovery" in discovery["requester_can"]
    assert "ask to connect the new guide to guides or stories that already exist" in discovery["requester_can"]

    policy = discovery["suggestion_policy"]
    assert policy["closed_vocabulary_forbidden"] is True
    assert policy["persistent_persona_required"] is False
    assert policy["requester_free_text_always_available"] is True
    assert policy["suggestions_do_not_become_product_ontology"] is True
    assert policy["max_visible_suggestions_default"] <= 3

    resolution = contract["existing_material_resolution"]
    assert "existing_qualified_guide_module" in resolution["candidate_sources"]
    assert "new_content_candidate" in resolution["candidate_sources"]
    assert "never a mandatory thematic profile" in resolution["no_lock_in"]


def test_runtime_interaction_is_separate_and_optional():
    contract = load("series/city-guide-factory-v1.1.json")
    runtime = contract["runtime_experience"]
    assert runtime["interactive_discovery"] == "OPTIONAL_PRODUCT_CAPABILITY"
    assert "separate from the mandatory creation-discovery process" in runtime["rule"]
    assert "must remain useful without runtime conversational interaction" in runtime["default"]


def test_bordeaux_is_only_a_fixture_for_the_generic_creation_contract():
    gate = load("series/bordeaux-discovery/creative-brief-gate-v1.1.json")
    assert gate["status"] == "ADJUST_ACCEPTED"
    assert gate["role"] == "VERTICAL_PROOF_FIXTURE_ONLY"
    assert gate["system_contract"] == "series/city-guide-factory-v1.1.json"
    assert gate["baseline"]["human_review"] == "PASS"
    assert gate["baseline"]["preserve"] is True
    assert gate["baseline"]["route_change_allowed"] is False
    assert "generic creation lifecycle of every guide module" in gate["human_direction"]
    assert "adding Bordeaux-specific workflow logic" in gate["proof_scope"]["must_not_prove_by"]
    assert gate["next_gate"] == "PROVE_GENERIC_MODULE_CREATION_DISCOVERY_USING_BORDEAUX_FIXTURE"


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
