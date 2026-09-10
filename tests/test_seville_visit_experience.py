import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "series" / "seville-discovery"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_visit_experience_covers_all_published_seville_episodes():
    series = load(BASE / "series.json")
    experience = load(BASE / "assets" / "visit-experience.json")

    assert experience["schema"] == "recit.visit-experience.v1"
    assert experience["series"] == "seville-discovery"
    assert experience["navigation_authority"] == "external_real_conditions"

    published_ids = {episode["id"] for episode in series["episodes"]}
    experience_ids = set(experience["episodes"])
    assert published_ids == experience_ids

    allowed = {"ARRIVAL", "LOOK", "STORY", "REVEAL", "MOVE", "SILENCE", "COMPARE", "HUMAN_STORY", "OPTIONAL_DEPTH", "EXIT"}
    for episode_id, field in experience["episodes"].items():
        assert field["why"].strip()
        assert field["look_first"].strip()
        assert field["field_minutes"] > 0
        assert field["cues"]
        assert all(cue["type"] in allowed for cue in field["cues"])
        assert any(cue["type"] in {"LOOK", "COMPARE", "REVEAL"} for cue in field["cues"]), episode_id


def test_advanced_visit_layer_is_additive_and_keeps_route_authority_external():
    experience = load(BASE / "assets" / "visit-experience.json")
    route = load(BASE / "assets" / "route-map.json")

    assert route["days"]
    assert experience["navigation_authority"] == "external_real_conditions"
    payload = json.dumps(experience, ensure_ascii=False).lower()
    assert "google maps" not in payload or "authority" not in payload


def test_web_companion_exposes_now_and_field_program_without_replacing_core_player():
    js = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8")
    app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")

    assert "Maintenant" in js
    assert "Regardez d’abord" in js
    assert "visit-experience.json" in js
    assert "data-play" in js
    assert "player-audio" in app
