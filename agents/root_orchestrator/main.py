from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header

from common.evidence import append_event, verify_chain
from common.identity import derive_actor_from_request
from common.models import Resource
from common.policy import evaluate
from common.rag import retrieve_permitted_context

app = FastAPI(title="Akretic Root Orchestrator")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "root-orchestrator"}


@app.post("/run_vendor_review")
def run_vendor_review(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
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

    retrieval = retrieve_permitted_context(
        query=payload.get("query", "VendorNova procurement security policy"),
        actor=actor,
        run_id=run_id,
        write_evidence=True,
    )

    side_effect_resource = Resource(
        resource_id="vendornova_exception_export",
        classification="internal",
        source_type="draft",
        allowed_groups=actor.groups,
        external_release_allowed=False,
        sensitivity_tags=("external-facing",),
    )
    export_decision = evaluate(
        actor=actor,
        action="export_external",
        resource=side_effect_resource,
        run_id=run_id,
    )
    append_event(
        run_id=run_id,
        actor=actor,
        agent_id="root_orchestrator",
        action="export_external",
        resource_id=side_effect_resource.resource_id,
        outcome=export_decision.outcome,
        reason=export_decision.reason,
        correlation_id=export_decision.correlation_id,
        metadata={"decision_id": export_decision.decision_id},
    )

    permitted_source_ids = [chunk["source_id"] for chunk in retrieval["chunks"]]
    summary = (
        "VendorNova review assembled from permitted synthetic context only. "
        f"Permitted sources: {', '.join(permitted_source_ids) or 'none'}. "
        f"External export decision: {export_decision.outcome}."
    )

    return {
        "run_id": run_id,
        "actor": actor.to_dict(),
        "retrieval": retrieval,
        "export_decision": export_decision.to_dict(),
        "summary": summary,
        "verification": verify_chain(run_id),
        "model_path_note": "ADK/Gemini integration should summarize only the permitted chunks returned here.",
    }
