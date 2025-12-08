import os
from fastapi.testclient import TestClient

os.environ.setdefault("GRAPH_DB_URI", "")
os.environ.setdefault("GRAPH_DB_USER", "")
os.environ.setdefault("GRAPH_DB_PASSWORD", "")

from src.main import app  # noqa: E402


def test_readyz_without_graph():
    client = TestClient(app)
    resp = client.get("/readyz")
    assert resp.status_code == 200
    body = resp.json()
    assert "graph" in body


def test_caps_roundtrip():
    client = TestClient(app)
    resp = client.post("/caps/report", json={"source": "test", "caps": {"demo": True}})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
