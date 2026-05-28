from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException

from common.approval import ApprovalStore
from common.evidence import append_event, read_events, verify_chain
from common.identity import derive_actor_from_request
from common.models import Resource

app = FastAPI(title="Akretic Approval/Evidence Agent")
CARD_PATH = Path(__file__).resolve().parent / "agent-card.json"
APPROVALS = ApprovalStore()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "approval-evidence-agent"}


@app.get("/agent-card.json")
@app.get("/.well-known/agent-card.json")
def agent_card() -> dict[str, Any]:
    return json.loads(CARD_PATH.read_text(encoding="utf-8"))


@app.post("/request_approval")
def request_approval(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    actor = derive_actor_from_request(demo_persona=x_akretic_persona or payload.get("persona"), body_claims=payload.get("actor"))
    resource = Resource.from_dict(payload.get("resource", {"resource_id": "external_exception", "classification": "internal", "source_type": "draft"}))
    approval = APPROVALS.create(
        actor=actor,
        action=payload.get("action", "export_external"),
        resource=resource,
        run_id=payload.get("run_id", "local-run"),
        draft_payload=payload.get("draft_payload", ""),
    )
    append_event(
        run_id=approval.run_id,
        actor=actor,
        agent_id="approval_evidence_agent",
        action="request_approval",
        resource_id=approval.resource_id,
        outcome="approval_required",
        reason="approval request created",
        metadata={"approval_id": approval.approval_id, "draft_payload_hash": approval.draft_payload_hash},
    )
    return approval.to_dict()


@app.post("/approvals/{approval_id}/decide")
def decide_approval(approval_id: str, payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    reviewer = derive_actor_from_request(demo_persona=x_akretic_persona or payload.get("persona", "security_reviewer"), body_claims=payload.get("actor"))
    try:
        approval = APPROVALS.decide(
            approval_id=approval_id,
            reviewer=reviewer,
            status=payload.get("status", "approved"),
            reason=payload.get("reason", "demo reviewer decision"),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    append_event(
        run_id=approval.run_id,
        actor=reviewer,
        agent_id="approval_evidence_agent",
        action="approve_action",
        resource_id=approval.resource_id,
        outcome=approval.status,
        reason=approval.decision_reason or "reviewer decision",
        metadata={"approval_id": approval.approval_id},
    )
    return approval.to_dict()


@app.post("/record_event")
def record_event(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    actor = derive_actor_from_request(demo_persona=x_akretic_persona or payload.get("persona"), body_claims=payload.get("actor"))
    return append_event(
        run_id=payload.get("run_id", "local-run"),
        actor=actor,
        agent_id=payload.get("agent_id", "unknown_agent"),
        action=payload.get("action", "unknown_action"),
        resource_id=payload.get("resource_id", "unknown_resource"),
        outcome=payload.get("outcome", "result"),
        reason=payload.get("reason", "event recorded"),
        correlation_id=payload.get("correlation_id"),
        metadata=payload.get("metadata", {}),
    )


@app.get("/verify/{run_id}")
def verify(run_id: str, x_akretic_persona: str | None = Header(default="admin")) -> dict[str, Any]:
    actor = derive_actor_from_request(demo_persona=x_akretic_persona or "admin")
    if actor.role not in {"admin", "security_reviewer"} and "admin" not in actor.groups:
        raise HTTPException(status_code=403, detail="verify requires admin or reviewer demo persona")
    return verify_chain(run_id)


@app.get("/evidence/{run_id}/report")
def report(run_id: str, x_akretic_persona: str | None = Header(default="admin")) -> dict[str, Any]:
    actor = derive_actor_from_request(demo_persona=x_akretic_persona or "admin")
    if actor.role not in {"admin", "security_reviewer"} and "admin" not in actor.groups:
        raise HTTPException(status_code=403, detail="report requires admin or reviewer demo persona")
    return {"run_id": run_id, "verification": verify_chain(run_id), "events": read_events(run_id)}
