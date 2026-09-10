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
    readiness = load("travel-readiness.json")

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

    luggage = plan["three_day_enrichment"]["sunday_luggage"]
    assert luggage["primary"]["address"].startswith("C. Agua, 5")
    assert luggage["primary"]["assessment"] == "VERIFIED_DEDICATED_LUGGAGE_STORAGE"
    assert "DO_NOT_DEPEND" in luggage["rejected_dependency"]["assessment"]
    assert readiness["confirmed"]["sunday_luggage"]["address"].startswith("C. Agua, 5")
    assert readiness["confirmed"]["sunday_airport_buffer"]["pickup_edge"] == "Puerta de la Carne / Avenida Menéndez Pelayo"

    day3 = route_map["days"][2]
    operational = json.dumps(day3, ensure_ascii=False)
    assert "C. Agua 5" in operational or "C. Agua%2C%205" in operational
    assert "Puerta de la Carne" in operational
    assert "C. Agua 7" not in operational

    public = json.dumps({"series": series, "plan": plan, "route_map": route_map, "readiness": readiness}, ensure_ascii=False).lower()
    for forbidden in ["passport", "passeport", "carte d’identité", "carte d'identité", "qr code", "réf. achat", "réf. réservation"]:
        assert forbidden not in public
