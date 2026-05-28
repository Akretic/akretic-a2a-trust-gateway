from __future__ import annotations

import asyncio

from agents.root_orchestrator.main import run_vendor_review_workflow
from common.evidence import read_events
from agents.approval_evidence_agent.main import app as approval_app
from services.gate0_lite.main import app as policy_app
from services.rag_dmz_lite.main import app as knowledge_app
from tests.service_utils import run_service


def test_root_calls_policy_and_knowledge_agents_over_a2a(monkeypatch, tmp_path):
    run_id = "test-a2a-root"
    monkeypatch.setenv("EVIDENCE_DIR", str(tmp_path))

    with run_service(policy_app) as policy_url:
        with run_service(knowledge_app) as knowledge_url:
            with run_service(approval_app) as approval_url:
                monkeypatch.setenv("POLICY_AGENT_URL", policy_url)
                monkeypatch.setenv("KNOWLEDGE_AGENT_URL", knowledge_url)
                monkeypatch.setenv("APPROVAL_EVIDENCE_URL", approval_url)
                result = asyncio.run(
                    run_vendor_review_workflow(
                        {
                            "run_id": run_id,
                            "persona": "procurement_user",
                            "query": "VendorNova procurement security policy",
                        },
                        x_akretic_persona="procurement_user",
                    )
                )

    events = read_events(run_id, path=tmp_path)
    a2a_events = [event for event in events if event["action"] == "a2a_call"]
    calls = {(event["metadata"]["callee"], event["metadata"]["skill"]) for event in a2a_events}
    policy_events = [event for event in events if event["agent_id"] == "policy_agent"]

    assert result["verification"]["valid"] is True
    assert result["retrieval"]["chunks"]
    assert "executive_acquisition_memo" in {
        source["source_id"] for source in result["retrieval"]["denied_sources"]
    }
    assert ("akretic-policy-agent", "authorize_intent") in calls
    assert ("akretic-knowledge-agent", "retrieve_permitted_context") in calls
    assert ("akretic-approval-evidence-agent", "request_approval") in calls
    assert {call["agent"] for call in result["a2a_calls"]}.issuperset(
        {
            "akretic-policy-agent",
            "akretic-knowledge-agent",
            "akretic-approval-evidence-agent",
        }
    )
    assert all(call["correlation_id"].startswith("corr_") for call in result["a2a_calls"])
    assert all(call["agent_card_resolved"] is True for call in result["a2a_calls"])
    assert result["approval_request"]["status"] == "pending"
    assert result["export_result"]["status"] == "blocked_pending_approval"
    assert all(event["correlation_id"].startswith("corr_") for event in a2a_events)
    assert all(event["metadata"]["caller"] == "root_orchestrator" for event in a2a_events)
    assert all(
        event["metadata"]["identity_source"] == "x-akretic-persona header"
        for event in a2a_events
    )
    assert {"allow", "approval_required"}.issubset({event["outcome"] for event in policy_events})
