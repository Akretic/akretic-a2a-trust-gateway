from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any

from google.adk import Workflow

from agents.root_orchestrator.main import run_vendor_review_workflow

PREFERRED_PUBLIC_WORDING = (
    "The current proof path runs on Cloud Run with Vertex/Gemini summarization "
    "and A2A Agent Card skill-call wiring. The root entrypoint uses a "
    "Google ADK Workflow wrapper that delegates to the verified orchestrator "
    "path. Authorization, retrieval filtering, approvals, and evidence remain "
    "outside Gemini and are not delegated to the model."
)


@dataclass(frozen=True)
class AdkRootInvocation:
    """ADK-shaped local invocation envelope for the verified VendorNova workflow.

    This wrapper is intentionally not a new runtime route. It adapts an agent-style
    request into the existing root orchestrator call so the same identity, policy,
    retrieval, approval, A2A, Gemini, and evidence controls remain authoritative.
    """

    user_message: str = "VendorNova procurement security policy"
    persona: str = "procurement_user"
    vendor: str = "VendorNova"
    run_id: str | None = None
    model_mode: str | None = None
    max_chunks: int | None = None
    body_claims: Mapping[str, Any] | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AdkRootInvocation":
        return cls(
            user_message=str(payload.get("user_message") or payload.get("query") or ""),
            persona=str(payload.get("persona") or "procurement_user"),
            vendor=str(payload.get("vendor") or "VendorNova"),
            run_id=payload.get("run_id"),
            model_mode=payload.get("model_mode"),
            max_chunks=payload.get("max_chunks"),
            body_claims=payload.get("body_claims") or payload.get("actor"),
        )

    def to_workflow_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "persona": self.persona,
            "query": self.user_message,
            "vendor": self.vendor,
        }
        if self.run_id:
            payload["run_id"] = self.run_id
        if self.model_mode:
            payload["model_mode"] = self.model_mode
        if self.max_chunks is not None:
            payload["max_chunks"] = self.max_chunks
        if self.body_claims is not None:
            payload["actor"] = dict(self.body_claims)
        return payload


def describe_adk_alignment() -> dict[str, Any]:
    """Return conservative ADK mapping metadata without overclaiming runtime scope."""
    return {
        "status": "adk_workflow_wrapper_delegates_to_verified_orchestrator",
        "google_adk_package": f"google-adk=={version('google-adk')}",
        "public_cloud_run_behavior_changed": True,
        "agent_runtime_or_registry_required": False,
        "delegated_to": "agents.root_orchestrator.main.run_vendor_review_workflow",
        "public_wording": PREFERRED_PUBLIC_WORDING,
        "root_agent_mapping": {
            "adk_concept": "root agent / workflow coordinator",
            "verified_component": "Root Orchestrator",
            "entrypoint": "run_vendor_review_workflow",
            "boundary": "delegates to existing Cloud Run proof path",
        },
        "tool_mappings": [
            {
                "adk_concept": "tool call",
                "verified_component": "Gate0-lite Policy Agent",
                "a2a_skill": "authorize_intent",
                "control": "policy outcome is deterministic and outside Gemini",
            },
            {
                "adk_concept": "tool call",
                "verified_component": "RAG DMZ-lite Knowledge Agent",
                "a2a_skill": "retrieve_permitted_context",
                "control": "restricted chunks are filtered before model context",
            },
            {
                "adk_concept": "human approval / tool result",
                "verified_component": "Approval/Evidence Agent",
                "a2a_skill": "request_approval",
                "control": "sensitive side effects remain pending until reviewer decision",
            },
            {
                "adk_concept": "model call",
                "verified_component": "Vertex/Gemini summarizer adapter",
                "a2a_skill": None,
                "control": "Gemini summarizes permitted context only and does not authorize",
            },
            {
                "adk_concept": "trace / event log",
                "verified_component": "hash-chained evidence ledger",
                "a2a_skill": "verify_chain",
                "control": "material decisions and outputs are recorded and verified",
            },
        ],
        "control_boundaries": [
            "derived_identity",
            "gate0_lite_policy",
            "rag_dmz_lite_pre_context_filtering",
            "approval_required_gate",
            "hash_chained_evidence",
            "a2a_agent_card_skill_calls",
        ],
        "non_claims": [
            "not a replacement for the verified root orchestrator",
            "not full ADK-native orchestration",
            "not Agent Runtime or Agent Registry integration",
            "not a new public workflow or product surface",
        ],
    }


async def adk_vendor_review_delegate(node_input: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """ADK function-node delegate for the existing VendorNova workflow."""
    return await run_adk_aligned_vendor_review(node_input or {})


def build_adk_root_workflow() -> Workflow:
    """Build the ADK Workflow wrapper used to prove root orchestration mapping."""
    return Workflow(
        name="akretic_root_vendor_review_workflow",
        description="ADK workflow wrapper delegating to the verified VendorNova root orchestrator.",
        edges=(("START", adk_vendor_review_delegate),),
    )


async def run_adk_aligned_vendor_review(
    invocation: AdkRootInvocation | Mapping[str, Any],
    *,
    x_akretic_persona: str | None = None,
) -> dict[str, Any]:
    """Run the ADK-aligned wrapper by delegating to the verified orchestrator."""
    request = (
        invocation
        if isinstance(invocation, AdkRootInvocation)
        else AdkRootInvocation.from_mapping(invocation)
    )
    workflow = build_adk_root_workflow()
    adk_package = f"google-adk=={version('google-adk')}"
    workflow_payload = {
        **request.to_workflow_payload(),
        "orchestration_wrapper": "google-adk-workflow",
        "adk_package": adk_package,
        "adk_workflow": workflow.name,
    }
    result = await run_vendor_review_workflow(
        workflow_payload,
        x_akretic_persona=x_akretic_persona or request.persona,
    )
    return {
        **result,
        "adk_alignment": {
            "status": "adk_workflow_wrapper_delegates_to_verified_orchestrator",
            "delegated_to": "agents.root_orchestrator.main.run_vendor_review_workflow",
            "public_cloud_run_behavior_changed": True,
            "runtime_replaced": False,
            "google_adk_package": adk_package,
            "workflow_name": workflow.name,
            "workflow_node": "adk_vendor_review_delegate",
            "control_boundaries": describe_adk_alignment()["control_boundaries"],
        },
        "adk_runtime": {
            "status": "active_wrapper_delegate",
            "package": adk_package,
            "workflow_name": workflow.name,
            "delegated_to": "run_vendor_review_workflow",
        },
    }
