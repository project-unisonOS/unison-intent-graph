from fastapi import FastAPI, Body
from typing import Any, Dict
import time
import logging
import os

from neo4j import GraphDatabase, basic_auth

app = FastAPI(title="unison-intent-graph")
_caps_latest: Dict[str, Any] = {}
_caps_updated_at: float | None = None
_gesture_latest: Dict[str, Any] = {}
logger = logging.getLogger("unison-intent-graph")

GRAPH_URI = os.getenv("GRAPH_DB_URI")
GRAPH_USER = os.getenv("GRAPH_DB_USER")
GRAPH_PASSWORD = os.getenv("GRAPH_DB_PASSWORD")
_GRAPH_DRIVER = None

if GRAPH_URI and GRAPH_USER and GRAPH_PASSWORD:
    try:
        _GRAPH_DRIVER = GraphDatabase.driver(
            GRAPH_URI, auth=basic_auth(GRAPH_USER, GRAPH_PASSWORD), max_connection_lifetime=60
        )
    except Exception:
        _GRAPH_DRIVER = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "unison-intent-graph"}


@app.get("/readyz")
def readyz():
    graph_ok = True
    if _GRAPH_DRIVER:
        try:
            with _GRAPH_DRIVER.session() as session:
                result = session.run("RETURN 1 as ok").single()
                graph_ok = bool(result.get("ok"))
        except Exception:
            graph_ok = False
    status = "ready" if graph_ok else "degraded"
    return {"status": status, "service": "unison-intent-graph", "graph": graph_ok}


@app.post("/caps/report")
def caps_report(body: Dict[str, Any] = Body(...)):
    """Cache the latest capability report for debugging/forwarding."""
    global _caps_latest, _caps_updated_at
    _caps_latest = body or {}
    _caps_updated_at = time.time()
    logger.info("caps.report received (intent-graph): %s", list(body.keys()))
    return {"ok": True, "stored": True, "updated_at": _caps_updated_at}


@app.get("/caps/latest")
def caps_latest():
    return {"ok": True, "caps": _caps_latest, "updated_at": _caps_updated_at}


@app.post("/gesture/select")
def gesture_select(body: Dict[str, Any] = Body(...)):
    """Record a simple touch/gesture selection event for downstream consumers."""
    global _gesture_latest
    now = time.time()
    gesture = {
        "person_id": body.get("person_id"),
        "card_id": body.get("card_id"),
        "card_title": body.get("card_title"),
        "ts": now,
    }
    _gesture_latest = gesture
    logger.info("gesture.select received (intent-graph): %s", gesture)
    return {"ok": True, "stored": True, "ts": now}


@app.get("/gesture/latest")
def gesture_latest():
    return {"ok": True, "gesture": _gesture_latest}


@app.post("/graph/intent")
def graph_intent(body: Dict[str, Any] = Body(...)):
    """Record an intent instance linking person and agent/resource in Neo4j (best-effort)."""
    if _GRAPH_DRIVER:
        intent_id = body.get("intent_id") or f"intent-{int(time.time()*1000)}"
        person_id = body.get("person_id")
        agent_id = body.get("agent_id")
        rel_type = body.get("rel_type", "HANDLES")
        try:
            with _GRAPH_DRIVER.session() as session:
                session.run(
                    """
                    MERGE (i:IntentInstance {id:$intent_id})
                    SET i.name=$name, i.created_at=timestamp()
                    MERGE (p:Person {id:$person_id})
                    MERGE (a:Agent {id:$agent_id})
                    MERGE (p)-[:REQUESTED]->(i)
                    MERGE (a)-[r:%s]->(i)
                    SET r.created_at=timestamp()
                    """
                    % rel_type,
                    intent_id=intent_id,
                    person_id=person_id,
                    agent_id=agent_id,
                    name=body.get("name"),
                )
        except Exception as exc:
            logger.warning("graph_intent error: %s", exc)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
