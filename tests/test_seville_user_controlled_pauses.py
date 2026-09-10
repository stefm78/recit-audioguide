import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "series" / "seville-discovery"


def test_pause_contract_is_explicit_and_bounded():
    data = json.loads((SERIES / "assets" / "visit-experience.json").read_text(encoding="utf-8"))
    assert data["schema"] == "recit.visit-experience.v2"
    assert data["pause_model"]["default"] == "HYBRID_MICRO_SILENCE_AND_USER_PAUSE"

    user_pauses = []
    for episode_id, episode in data["episodes"].items():
        for cue in episode.get("cues", []):
            if cue.get("type") == "USER_PAUSE":
                user_pauses.append((episode_id, cue["text"]))

    assert 5 <= len(user_pauses) <= 8
    assert all("pause" in text.lower() for _, text in user_pauses)
    assert all("repr" in text.lower() or "relance" in text.lower() for _, text in user_pauses)


def test_major_user_pauses_are_spoken_in_production_scripts():
    ids = [
        "seville-discovery-ep06",
        "seville-discovery-ep04",
        "seville-discovery-ep02",
        "seville-discovery-ep05",
        "seville-discovery-ep01",
        "seville-discovery-g02",
        "seville-discovery-g13",
    ]
    for episode_id in ids:
        script = json.loads((SERIES / "audio" / f"{episode_id}.json").read_text(encoding="utf-8"))
        speech = " ".join(segment["text"] for segment in script["segments"]).lower()
        assert "pause" in speech, episode_id
        assert "relance" in speech or "reprenez" in speech, episode_id


def test_mobile_surface_distinguishes_pause_semantics():
    js = (ROOT / "web" / "next-step.js").read_text(encoding="utf-8")
    assert "USER_PAUSE:'Pause libre · reprenez quand vous voulez'" in js
    assert "MICRO_SILENCE:'Respiration'" in js
    assert ".cue-user_pause" in js
