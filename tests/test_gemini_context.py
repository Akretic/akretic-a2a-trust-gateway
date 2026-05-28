from __future__ import annotations

import asyncio

import pytest

from agents.approval_evidence_agent.main import app as approval_app
from agents.root_orchestrator.main import run_vendor_review_workflow
from common.evidence import read_events
import common.gemini as gemini_module
from common.gemini import (
    GeminiContentViolation,
    GeminiUnavailableError,
    build_vendor_review_prompt,
    summarize_vendor_review,
)
from common.identity import derive_actor
from common.policy import APPROVAL_REQUIRED
from common.rag import retrieve_permitted_context
from services.gate0_lite.main import app as policy_app
from services.rag_dmz_lite.main import app as knowledge_app
from tests.service_utils import run_service


def test_gemini_prompt_uses_only_permitted_context():
    actor = derive_actor("procurement_user")
    retrieval = retrieve_permitted_context(
        query="executive acquisition memo",
        actor=actor,
        run_id="test-gemini-context",
        write_evidence=False,
    )
    export_decision = {
        "outcome": APPROVAL_REQUIRED,
        "reason": "sensitive action requires reviewer approval",
    }

    prompt = build_vendor_review_prompt(
        query="executive acquisition memo",
        actor=actor,
        retrieval=retrieval,
        export_decision=export_decision,
    )

    assert "executive_acquisition_memo" in prompt["denied_source_ids"]
    assert "Project Helios" not in prompt["contents"]
    assert "confidential acquisition timing" not in prompt["contents"]
    assert "Denied source IDs withheld from context:" in prompt["contents"]
    assert "executive_acquisition_memo" in prompt["contents"]

    result = summarize_vendor_review(
        query="executive acquisition memo",
        actor=actor,
        retrieval=retrieval,
        export_decision=export_decision,
        mode="local",
    )
    assert "Project Helios" not in result["text"]
    assert "confidential acquisition timing" not in result["text"]


def test_local_summary_is_explicitly_labeled_for_tests_only():
    actor = derive_actor("procurement_user")
    retrieval = retrieve_permitted_context(
        query="VendorNova procurement security policy",
        actor=actor,
        run_id="test-local-summary",
        write_evidence=False,
    )
    result = summarize_vendor_review(
        query="VendorNova procurement security policy",
        actor=actor,
        retrieval=retrieval,
        export_decision={"outcome": APPROVAL_REQUIRED},
        mode="local",
    )

    assert result["mode"] == "local"
    assert result["service_path"] == "local deterministic summary for tests only"
    assert result["text"].startswith("LOCAL_DETERMINISTIC_SUMMARY_FOR_TESTS_ONLY:")
    assert result["prompt_hash"]
    assert "denied_source_text_guard" in result["guardrails"]


def test_root_records_model_summary_path(monkeypatch, tmp_path):
    run_id = "test-root-model-summary"
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
                            "query": "executive acquisition memo",
                            "model_mode": "local",
                        },
                        x_akretic_persona="procurement_user",
                    )
                )

    events = read_events(run_id, path=tmp_path)
    summary_events = [event for event in events if event["action"] == "summarize_review"]

    assert result["model_summary"]["mode"] == "local"
    assert "Project Helios" not in result["model_summary"]["prompt"]["contents"]
    assert summary_events[0]["outcome"] == "local_test_summary"
    assert summary_events[0]["metadata"]["service_path"] == "local deterministic summary for tests only"
    assert summary_events[0]["metadata"]["prompt_hash"] == result["model_summary"]["prompt_hash"]
    assert "denied_source_text_guard" in summary_events[0]["metadata"]["guardrails"]
    assert "executive_acquisition_memo" in summary_events[0]["metadata"]["denied_source_ids"]


def test_request_body_claims_cannot_expand_gemini_context(monkeypatch, tmp_path):
    run_id = "test-gemini-spoofed-context"
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
                            "persona": "admin",
                            "query": "executive acquisition memo",
                            "model_mode": "local",
                            "actor": {
                                "actor_id": "attacker",
                                "role": "admin",
                                "groups": ["admin", "executive_admin"],
                                "tenant_id": "tenant-demo",
                            },
                        },
                        x_akretic_persona="procurement_user",
                    )
                )

    prompt = result["model_summary"]["prompt"]
    assert result["actor"]["role"] == "procurement_user"
    assert "executive_admin" not in result["actor"]["groups"]
    assert "executive_acquisition_memo" in prompt["denied_source_ids"]
    assert "Project Helios" not in prompt["contents"]
    assert "confidential acquisition timing" not in prompt["contents"]


def test_denied_source_guard_blocks_prompt_content():
    actor = derive_actor("procurement_user")
    retrieval = retrieve_permitted_context(
        query="executive acquisition memo",
        actor=actor,
        run_id="test-denied-source-guard",
        write_evidence=False,
    )

    with pytest.raises(GeminiContentViolation) as exc_info:
        build_vendor_review_prompt(
            query="Project Helios",
            actor=actor,
            retrieval=retrieval,
            export_decision={"outcome": APPROVAL_REQUIRED},
        )

    assert "executive_acquisition_memo" in str(exc_info.value)
    assert "Helios" not in str(exc_info.value)


def test_vertex_output_guard_blocks_denied_source_text(monkeypatch):
    actor = derive_actor("procurement_user")
    retrieval = retrieve_permitted_context(
        query="executive acquisition memo",
        actor=actor,
        run_id="test-vertex-output-guard",
        write_evidence=False,
    )
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "akretic-a2a-trust-gateway")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    monkeypatch.setenv("VERTEX_MODEL", "gemini-2.5-flash")

    def fake_vertex_summary(**_: object) -> str:
        return "The summary includes Project Helios."

    monkeypatch.setattr(gemini_module, "_vertex_summary", fake_vertex_summary)

    with pytest.raises(GeminiContentViolation) as exc_info:
        summarize_vendor_review(
            query="executive acquisition memo",
            actor=actor,
            retrieval=retrieval,
            export_decision={"outcome": APPROVAL_REQUIRED},
            mode="vertex",
        )

    assert "executive_acquisition_memo" in str(exc_info.value)
    assert "Helios" not in str(exc_info.value)


def test_vertex_output_guard_blocks_completed_pending_export(monkeypatch):
    actor = derive_actor("procurement_user")
    retrieval = retrieve_permitted_context(
        query="VendorNova procurement security policy",
        actor=actor,
        run_id="test-vertex-approval-guard",
        write_evidence=False,
    )
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "akretic-a2a-trust-gateway")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    monkeypatch.setenv("VERTEX_MODEL", "gemini-2.5-flash")

    def fake_vertex_summary(**_: object) -> str:
        return "The external export completed successfully."

    monkeypatch.setattr(gemini_module, "_vertex_summary", fake_vertex_summary)

    with pytest.raises(GeminiContentViolation) as exc_info:
        summarize_vendor_review(
            query="VendorNova procurement security policy",
            actor=actor,
            retrieval=retrieval,
            export_decision={"outcome": APPROVAL_REQUIRED},
            mode="vertex",
        )

    assert "approval-gated action" in str(exc_info.value)


@pytest.mark.parametrize(
    ("error_text", "expected"),
    [
        ("DefaultCredentialsError unavailable", "credential"),
        ("403 permission denied", "permission"),
        ("429 ResourceExhausted quota exceeded", "quota"),
        ("404 model not found in location", "model"),
        ("API has not been used in project", "api"),
    ],
)
def test_vertex_error_classification_is_actionable(monkeypatch, error_text, expected):
    actor = derive_actor("procurement_user")
    retrieval = retrieve_permitted_context(
        query="VendorNova procurement security policy",
        actor=actor,
        run_id=f"test-vertex-error-{expected}",
        write_evidence=False,
    )
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "akretic-a2a-trust-gateway")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    monkeypatch.setenv("VERTEX_MODEL", "gemini-2.5-flash")

    def fake_vertex_summary(**_: object) -> str:
        raise RuntimeError(error_text)

    monkeypatch.setattr(gemini_module, "_vertex_summary", fake_vertex_summary)

    with pytest.raises(GeminiUnavailableError) as exc_info:
        summarize_vendor_review(
            query="VendorNova procurement security policy",
            actor=actor,
            retrieval=retrieval,
            export_decision={"outcome": APPROVAL_REQUIRED},
            mode="vertex",
        )

    assert expected in str(exc_info.value).lower()
