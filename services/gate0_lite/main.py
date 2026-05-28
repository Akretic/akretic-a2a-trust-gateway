from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header

from common.identity import derive_actor_from_request
from common.models import Resource
from common.policy import evaluate

app = FastAPI(title="Akretic Gate0-lite / Policy Agent")
CARD_PATH = Path(__file__).resolve().parents[2] / "agents" / "policy_agent" / "agent-card.json"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "gate0-lite"}


@app.get("/agent-card.json")
@app.get("/.well-known/agent-card.json")
def agent_card() -> dict[str, Any]:
    return json.loads(CARD_PATH.read_text(encoding="utf-8"))


@app.post("/authorize_intent")
def authorize_intent(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    actor = derive_actor_from_request(demo_persona=x_akretic_persona or payload.get("persona"), body_claims=payload.get("actor"))
    resource = Resource.from_dict(payload.get("resource", {"resource_id": "unknown", "classification": "internal", "source_type": "unknown"}))
    decision = evaluate(
        actor=actor,
        action=payload.get("action", "unknown"),
        resource=resource,
        run_id=payload.get("run_id", "local-run"),
        context=payload.get("context", {}),
        correlation_id=payload.get("correlation_id"),
    )
    return decision.to_dict()


@app.post("/classify_resource")
def classify_resource(payload: dict[str, Any]) -> dict[str, Any]:
    resource = Resource.from_dict(payload.get("resource", {}))
    return resource.to_dict()


@app.post("/explain_decision")
def explain_decision(payload: dict[str, Any]) -> dict[str, Any]:
    return {"explanation": payload.get("reason", "Policy decision reason not supplied."), "source": "gate0-lite"}
