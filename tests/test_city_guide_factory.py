import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "city_guide_factory", ROOT / "tools" / "city_guide_factory.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def load_proposal():
    return json.loads(
        (ROOT / "series" / "bordeaux-discovery" / "proposal.json").read_text(encoding="utf-8")
    )


def test_bordeaux_proposal_reaches_human_gate():
    assert MODULE.validate(load_proposal()) == []


def test_pre_gate_proposal_rejects_audio_fields():
    proposal = load_proposal()
    proposal["route"][0]["audio_url"] = "https://example.invalid/audio.mp3"
    errors = MODULE.validate(proposal)
    assert any("must not contain audio fields" in error for error in errors)


def test_downstream_must_remain_blocked_before_gate():
    proposal = load_proposal()
    proposal["downstream"]["scripts"] = "READY"
    errors = MODULE.validate(proposal)
    assert any("downstream.scripts" in error for error in errors)
