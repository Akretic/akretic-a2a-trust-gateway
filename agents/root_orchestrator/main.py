from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header

from common.a2a_client import call_skill
from common.evidence import append_event, verify_chain
from common.identity import derive_actor_from_request
from common.models import Actor
from common.models import Resource

app = FastAPI(title="Akretic Root Orchestrator")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "root-orchestrator"}


def _agent_url(env_name: str, default: str) -> str:
    return os.getenv(env_name, default)


def _record_policy_decision(*, actor: Actor, decision: dict[str, Any]) -> dict[str, Any]:
    resource = decision.get("resource", {})
    return append_event(
        run_id=decision.get("run_id", "local-run"),
        actor=actor,
        agent_id="policy_agent",
        action=decision.get("action", "unknown"),
        resource_id=resource.get("resource_id", "unknown_resource"),
        outcome=decision.get("outcome", "unknown"),
        reason=decision.get("reason", "policy decision returned"),
        correlation_id=decision.get("correlation_id"),
        metadata={"decision_id": decision.get("decision_id")},
    )


async def run_vendor_review_workflow(
    payload: dict[str, Any],
    x_akretic_persona: str | None = None,
) -> dict[str, Any]:
    """Local deterministic orchestration path.

    Codex ticket T09 should replace/augment the final summarization with ADK/Gemini through Vertex AI.
    Do not let Gemini authorize. This endpoint keeps the P0 proof chain testable without external services.
    """
    run_id = payload.get("run_id") or f"run_{uuid4().hex}"
    persona = x_akretic_persona or payload.get("persona") or os.getenv("AKRETIC_DEMO_PERSONA", "procurement_user")
    actor = derive_actor_from_request(demo_persona=persona, body_claims=payload.get("actor"))

    append_event(
        run_id=run_id,
        actor=actor,
        agent_id="root_orchestrator",
        action="start_vendor_review",
        resource_id=payload.get("vendor", "VendorNova"),
        outcome="started",
        reason="vendor-risk review started",
    )

    identity_headers = {"x-akretic-persona": persona}
    policy_url = _agent_url("POLICY_AGENT_URL", "http://127.0.0.1:8101")
    knowledge_url = _agent_url("KNOWLEDGE_AGENT_URL", "http://127.0.0.1:8102")
    query = payload.get("query", "VendorNova procurement security policy")

    retrieval_resource = Resource(
        resource_id="vendornova_review_context",
        classification="internal",
        source_type="workflow",
        allowed_groups=actor.groups,
        external_release_allowed=False,
    )
    retrieval_decision = await call_skill(
        base_url=policy_url,
        skill="authorize_intent",
        payload={
            "persona": persona,
            "action": "retrieve_internal",
            "resource": retrieval_resource.to_dict(),
            "context": {"query": query},
        },
        run_id=run_id,
        caller_agent_id="root_orchestrator",
        actor=actor,
        headers=identity_headers,
    )
    _record_policy_decision(actor=actor, decision=retrieval_decision)

    if retrieval_decision["outcome"] == "allow":
        retrieval = await call_skill(
            base_url=knowledge_url,
            skill="retrieve_permitted_context",
            payload={
                "persona": persona,
                "query": query,
                "max_chunks": int(payload.get("max_chunks", 5)),
                "write_evidence": True,
            },
            run_id=run_id,
            caller_agent_id="root_orchestrator",
            actor=actor,
            headers=identity_headers,
        )
    else:
        retrieval = {
            "run_id": run_id,
            "actor_id": actor.actor_id,
            "query": query,
            "chunks": [],
            "denied_sources": [
                {
                    "source_id": retrieval_resource.resource_id,
                    "classification": retrieval_resource.classification,
                    "reason": retrieval_decision["reason"],
                    "decision_id": retrieval_decision["decision_id"],
                }
            ],
            "correlation_id": retrieval_decision["correlation_id"],
        }

    side_effect_resource = Resource(
        resource_id="vendornova_exception_export",
        classification="internal",
        source_type="draft",
        allowed_groups=actor.groups,
        external_release_allowed=False,
        sensitivity_tags=("external-facing",),
    )
    export_decision = await call_skill(
        base_url=policy_url,
        skill="authorize_intent",
        payload={
            "persona": persona,
            "action": "export_external",
            "resource": side_effect_resource.to_dict(),
            "context": {"query": query},
        },
        run_id=run_id,
        caller_agent_id="root_orchestrator",
        actor=actor,
        headers=identity_headers,
    )
    _record_policy_decision(actor=actor, decision=export_decision)
    append_event(
        run_id=run_id,
        actor=actor,
        agent_id="root_orchestrator",
        action="export_external",
        resource_id=side_effect_resource.resource_id,
        outcome=export_decision["outcome"],
        reason=export_decision["reason"],
        correlation_id=export_decision["correlation_id"],
        metadata={"decision_id": export_decision["decision_id"]},
    )

    permitted_source_ids = [chunk["source_id"] for chunk in retrieval["chunks"]]
    summary = (
        "VendorNova review assembled from permitted synthetic context only. "
        f"Permitted sources: {', '.join(permitted_source_ids) or 'none'}. "
        f"External export decision: {export_decision['outcome']}."
    )

    return {
        "run_id": run_id,
        "actor": actor.to_dict(),
        "retrieval_decision": retrieval_decision,
        "retrieval": retrieval,
        "export_decision": export_decision,
        "summary": summary,
        "verification": verify_chain(run_id),
        "model_path_note": "ADK/Gemini integration should summarize only the permitted chunks returned here.",
    }


@app.post("/run_vendor_review")
async def run_vendor_review(
    payload: dict[str, Any],
    x_akretic_persona: str | None = Header(default=None),
) -> dict[str, Any]:
    return await run_vendor_review_workflow(payload, x_akretic_persona=x_akretic_persona)
