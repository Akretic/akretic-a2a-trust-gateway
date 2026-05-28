from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException

from common.approval import ApprovalStore
from common.evidence import append_event, build_evidence_report, verify_chain
from common.identity import derive_actor_from_request
from common.models import Resource
from common.policy import ALLOW, evaluate

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


def _authorize_evidence_action(*, run_id: str, action: str, persona: str | None):
    actor = derive_actor_from_request(demo_persona=persona)
    resource = Resource(
        resource_id=run_id,
        classification="internal",
        source_type="evidence_ledger",
        allowed_groups=("admin", "security_reviewer"),
    )
    decision = evaluate(actor=actor, action=action, resource=resource, run_id=run_id)
    append_event(
        run_id=run_id,
        actor=actor,
        agent_id="approval_evidence_agent",
        action=action,
        resource_id=run_id,
        outcome=decision.outcome,
        reason=decision.reason,
        correlation_id=decision.correlation_id,
        metadata={"decision_id": decision.decision_id},
    )
    if decision.outcome != ALLOW:
        raise HTTPException(status_code=403, detail=decision.reason)
    return actor


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
        correlation_id=payload.get("correlation_id"),
        metadata={"approval_id": approval.approval_id, "draft_payload_hash": approval.draft_payload_hash},
    )
    return approval.to_dict()


def _decide_approval(
    *,
    approval_id: str,
    payload: dict[str, Any],
    x_akretic_persona: str | None,
) -> dict[str, Any]:
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
        correlation_id=payload.get("correlation_id"),
        metadata={"approval_id": approval.approval_id},
    )
    return approval.to_dict()


@app.post("/decide_approval")
def decide_approval_skill(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    return _decide_approval(
        approval_id=payload.get("approval_id", ""),
        payload=payload,
        x_akretic_persona=x_akretic_persona,
    )


@app.post("/approvals/{approval_id}/decide")
def decide_approval_path(
    approval_id: str,
    payload: dict[str, Any],
    x_akretic_persona: str | None = Header(default=None),
) -> dict[str, Any]:
    return _decide_approval(
        approval_id=approval_id,
        payload=payload,
        x_akretic_persona=x_akretic_persona,
    )


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
def verify(run_id: str, x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    _authorize_evidence_action(run_id=run_id, action="verify_evidence", persona=x_akretic_persona)
    return verify_chain(run_id)


@app.post("/verify_chain")
def verify_chain_skill(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    run_id = payload.get("run_id", "local-run")
    _authorize_evidence_action(run_id=run_id, action="verify_evidence", persona=x_akretic_persona)
    return verify_chain(run_id)


@app.get("/evidence/{run_id}/report")
def report(run_id: str, x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    _authorize_evidence_action(run_id=run_id, action="generate_report", persona=x_akretic_persona)
    return build_evidence_report(run_id)


@app.post("/generate_report")
def generate_report_skill(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    run_id = payload.get("run_id", "local-run")
    _authorize_evidence_action(run_id=run_id, action="generate_report", persona=x_akretic_persona)
    return build_evidence_report(run_id)
