from fastapi import FastAPI, Body
from typing import Any, Dict
import time
import logging

app = FastAPI(title="unison-intent-graph")
_caps_latest: Dict[str, Any] = {}
_caps_updated_at: float | None = None
logger = logging.getLogger("unison-intent-graph")


@app.get("/health")
def health():
    return {"status": "ok", "service": "unison-intent-graph"}


@app.get("/readyz")
def readyz():
    # Mirror health endpoint so compose healthcheck succeeds
    return {"status": "ready", "service": "unison-intent-graph"}


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
