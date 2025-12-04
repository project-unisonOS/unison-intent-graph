import pathlib
import sys

from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from main import app  # noqa: E402


def test_gesture_select_round_trip():
    client = TestClient(app)
    payload = {"person_id": "p1", "card_id": "card-123", "card_title": "Demo card"}
    resp = client.post("/gesture/select", json=payload)
    assert resp.status_code == 200
    assert resp.json().get("ok") is True

    latest = client.get("/gesture/latest")
    assert latest.status_code == 200
    body = latest.json()
    assert body.get("ok") is True
    gesture = body.get("gesture") or {}
    assert gesture.get("person_id") == "p1"
    assert gesture.get("card_id") == "card-123"
    assert gesture.get("card_title") == "Demo card"

