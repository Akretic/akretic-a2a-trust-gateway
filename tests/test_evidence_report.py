from __future__ import annotations

import asyncio

import httpx

from agents.approval_evidence_agent.main import app as approval_app
from agents.root_orchestrator.main import run_vendor_review_workflow
from services.gate0_lite.main import app as policy_app
from services.rag_dmz_lite.main import app as knowledge_app
from tests.service_utils import run_service


def test_evidence_report_contains_p0_proof_sections(monkeypatch, tmp_path):
    run_id = "test-evidence-report"
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
                            "model_mode": "local",
                        },
                        x_akretic_persona="procurement_user",
                    )
                )

                no_role_report = httpx.get(f"{approval_url}/evidence/{run_id}/report", timeout=5.0)
                assert no_role_report.status_code == 403

                decision_response = httpx.post(
                    f"{approval_url}/decide_approval",
                    json={
                        "approval_id": result["approval_request"]["approval_id"],
                        "status": "approved",
                        "reason": "approved for evidence report test",
                    },
                    headers={"x-akretic-persona": "security_reviewer"},
                    timeout=5.0,
                )
                decision_response.raise_for_status()

                report_response = httpx.get(
                    f"{approval_url}/evidence/{run_id}/report",
                    headers={"x-akretic-persona": "security_reviewer"},
                    timeout=5.0,
                )
                report_response.raise_for_status()
                report = report_response.json()

    summary = report["summary"]
    assert report["verification"]["valid"] is True
    assert summary["a2a_call_count"] >= 3
    assert summary["result_event_count"] >= 3
    assert "executive_acquisition_memo" in summary["retrieval_deny_source_ids"]
    assert "procurement_policy" in summary["retrieval_allow_source_ids"]
    assert "export_external" in summary["approval_required_actions"]
    assert summary["model_event_count"] == 1
    assert summary["model_modes"] == ["local"]
    assert summary["latest_model"]["mode"] == "local"
    assert summary["latest_model"]["model"] == "local-deterministic-test-summary"
    assert summary["latest_model"]["service_path"] == "local deterministic summary for tests only"
    assert summary["latest_model"]["prompt_hash"]
    assert "denied_source_text_guard" in summary["latest_model"]["guardrails"]
    assert "executive_acquisition_memo" in summary["latest_model"]["denied_source_ids"]
    assert len(report["model_events"]) == 1
    assert summary["reviewer_decisions"] == [
        {
            "resource_id": "vendornova_exception_export",
            "outcome": "approved",
            "actor_id": "user-security-001",
        }
    ]
    assert any(event["action"] == "generate_report" for event in report["events"])
