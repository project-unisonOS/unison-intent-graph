import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "unison-common" / "src"))
sys.path.append(str(ROOT / "unison-intent-graph" / "src"))

GRAPH_URI = os.getenv("GRAPH_DB_URI")
GRAPH_USER = os.getenv("GRAPH_DB_USER")
GRAPH_PASSWORD = os.getenv("GRAPH_DB_PASSWORD")

if not (GRAPH_URI and GRAPH_USER and GRAPH_PASSWORD):
    pytest.skip("Neo4j not configured", allow_module_level=True)

from src.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


def test_intent_graph_write(client):
    resp = client.post(
        "/graph/intent",
        json={"intent_id": "intent-test", "person_id": "person-test", "agent_id": "agent-test", "name": "demo"},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
