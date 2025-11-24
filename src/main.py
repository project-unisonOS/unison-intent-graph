from fastapi import FastAPI

app = FastAPI(title="unison-intent-graph")


@app.get("/health")
def health():
    return {"status": "ok", "service": "unison-intent-graph"}


@app.get("/readyz")
def readyz():
    # Mirror health endpoint so compose healthcheck succeeds
    return {"status": "ready", "service": "unison-intent-graph"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
