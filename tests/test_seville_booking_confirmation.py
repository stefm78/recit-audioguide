import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "series" / "seville-discovery"


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_confirmed_bookings_are_public_safe_and_consistent():
    series = load("series.json")
    plan = load("final-plan.json")
    route_map = load("assets/route-map.json")

    booking = series["visit"]["booking"]
    confirmed = plan["three_day_enrichment"]["confirmed_bookings"]

    assert booking["party_size"] == 2
    assert booking["cathedral"]["date"] == "2026-09-18"
    assert booking["cathedral"]["time"] == "12:10"
    assert booking["cathedral"]["status"] == "BOOKED_CONFIRMED"
    assert booking["alcazar"]["date"] == "2026-09-18"
    assert booking["alcazar"]["time"] == "17:00"
    assert booking["alcazar"]["status"] == "BOOKED_CONFIRMED"

    assert confirmed["party_size"] == 2
    assert confirmed["cathedral"]["time"] == "12:10"
    assert confirmed["alcazar"]["time"] == "17:00"

    day1 = route_map["days"][0]
    cathedral_leg = next(leg for leg in day1["legs"] if leg.get("audio_episode_id") == "seville-discovery-ep04")
    alcazar_leg = next(leg for leg in day1["legs"] if leg.get("audio_episode_id") == "seville-discovery-ep02")
    assert "12 h 10" in cathedral_leg["instructions"]
    assert "17 h" in alcazar_leg["instructions"]

    public = json.dumps({"series": series, "plan": plan, "route_map": route_map}, ensure_ascii=False).lower()
    for forbidden in ["passport", "passeport", "carte d’identité", "carte d'identité", "qr code", "réf. achat", "réf. réservation"]:
        assert forbidden not in public
