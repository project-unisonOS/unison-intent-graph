# unison-intent-graph

Intent graph front-end that sits ahead of the orchestrator, intended to manage intent routing and graph state.

## Status
Core (active, early) — placeholder FastAPI service used by devstack on port `8080`; expect rapid iteration.

## Run
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -c ../constraints.txt -r requirements.txt
python src/main.py
```

## Testing
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -c ../constraints.txt -r requirements.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OTEL_SDK_DISABLED=true python -m pytest
```

## Docs

Full docs at https://project-unisonos.github.io

## Integration
- Talks to `unison-context-graph` and `unison-orchestrator` per devstack wiring.
- Health endpoints: `/health`, `/readyz`.
- Receives `caps.report` and `gesture.select` events from I/O and renderer layers.

## Architecture Snapshot
- Receives intents/events from upstream clients (renderer/agent).
- Consults `unison-context-graph` for situational context.
- Forwards orchestrated decisions to `unison-orchestrator`.
- Caches lightweight state in Redis when available.

## Sample Flow
```bash
# Refresh env to match devstack defaults
cp .env.example .env
python src/main.py

# Probe health
curl http://localhost:8080/health

# Caps report (from IO services)
curl -X POST http://localhost:8080/caps/report -d '{"source":"io-core","caps":{"audio_in":{"present":true}}}' -H "Content-Type: application/json"

# Touch/gesture selection (from renderer)
curl -X POST http://localhost:8080/gesture/select -d '{"person_id":"local-user","card_id":"card-1","card_title":"Demo"}' -H "Content-Type: application/json"
```
