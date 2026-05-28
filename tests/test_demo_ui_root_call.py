from __future__ import annotations

import asyncio

from demo_ui import main as demo_ui


def test_demo_ui_calls_remote_root_when_configured(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"run_id": "remote-run", "summary": "remote root result"}

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, json, headers):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": self.timeout})
            return FakeResponse()

    monkeypatch.setenv("ROOT_ORCHESTRATOR_URL", "https://root.example")
    monkeypatch.delenv("AKRETIC_CLOUD_RUN_AUTH", raising=False)
    monkeypatch.setattr(demo_ui.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(demo_ui.run_review_from_ui("security_reviewer", "VendorNova"))

    assert result["run_id"] == "remote-run"
    assert calls == [
        {
            "url": "https://root.example/run_vendor_review",
            "json": {"persona": "security_reviewer", "query": "VendorNova"},
            "headers": {"x-akretic-persona": "security_reviewer"},
            "timeout": 45.0,
        }
    ]


def test_demo_ui_approval_calls_private_service_with_auth_headers(monkeypatch):
    calls = []

    class FakeResponse:
        def __init__(self, body, status_code=200):
            self._body = body
            self.status_code = status_code
            self.text = "error"

        def json(self):
            return self._body

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, json, headers):
            calls.append({"method": "POST", "url": url, "json": json, "headers": headers})
            return FakeResponse({"status": "approved"})

        async def get(self, url, headers):
            calls.append({"method": "GET", "url": url, "headers": headers})
            return FakeResponse({"valid": True})

    def fake_auth_headers(base_url, headers):
        return {**headers, "Authorization": f"Bearer token-for-{base_url}"}

    monkeypatch.setenv("APPROVAL_EVIDENCE_URL", "https://approval.example")
    monkeypatch.setattr(demo_ui.httpx, "AsyncClient", FakeClient)
    monkeypatch.setattr(demo_ui, "cloud_run_auth_headers", fake_auth_headers)

    decision, verification = asyncio.run(
        demo_ui.decide_approval_from_ui(
            run_id="run-1",
            approval_id="approval-1",
            reviewer_persona="security_reviewer",
            status="approved",
            reason="demo reviewer decision",
        )
    )

    assert decision == {"status": "approved"}
    assert verification == {"valid": True}
    assert calls == [
        {
            "method": "POST",
            "url": "https://approval.example/decide_approval",
            "json": {
                "approval_id": "approval-1",
                "status": "approved",
                "reason": "demo reviewer decision",
            },
            "headers": {
                "x-akretic-persona": "security_reviewer",
                "Authorization": "Bearer token-for-https://approval.example",
            },
        },
        {
            "method": "GET",
            "url": "https://approval.example/verify/run-1",
            "headers": {
                "x-akretic-persona": "security_reviewer",
                "Authorization": "Bearer token-for-https://approval.example",
            },
        },
    ]


def test_demo_ui_review_result_shows_p1_proof_markers():
    result = {
        "run_id": "run-p1",
        "summary": "VendorNova review assembled from permitted synthetic context only.",
        "retrieval_decision": {"outcome": "allow", "correlation_id": "corr-policy-read"},
        "retrieval": {
            "chunks": [{"source_id": "procurement_policy"}],
            "denied_sources": [{"source_id": "executive_acquisition_memo"}],
            "correlation_id": "corr-rag",
        },
        "export_decision": {
            "outcome": "approval_required",
            "reason": "external export requires reviewer approval",
            "correlation_id": "corr-policy-export",
        },
        "approval_request": {"approval_id": "approval-p1", "status": "pending"},
        "export_result": {"status": "blocked_pending_approval"},
        "verification": {"valid": True, "event_count": 12, "head_hash": "abc"},
        "model_summary": {
            "mode": "local",
            "service_path": "local deterministic summary for tests only",
        },
        "a2a_calls": [
            {
                "agent": "akretic-policy-agent",
                "skill": "authorize_intent",
                "correlation_id": "corr-policy-read",
                "outcome": "allow",
                "agent_card_resolved": True,
            },
            {
                "agent": "akretic-knowledge-agent",
                "skill": "retrieve_permitted_context",
                "correlation_id": "corr-rag",
                "outcome": "result",
                "agent_card_resolved": True,
            },
            {
                "agent": "akretic-approval-evidence-agent",
                "skill": "request_approval",
                "correlation_id": "corr-approval",
                "outcome": "approval_required",
                "agent_card_resolved": True,
            },
        ],
    }

    html = demo_ui._render_review_result(result, persona="procurement_user")

    assert "Judge walkthrough" in html
    assert "Denied before model context: executive_acquisition_memo." in html
    assert "external action is approval_required" in html
    assert "approval_required: external/sensitive action is paused." in html
    assert "Agent Card resolved" in html
    assert "correlation_id" in html
    assert "valid hash chain" in html
    assert "Evidence proof: valid hash chain." in html
    assert "Challenge prototype" in html
    assert "Synthetic data" in html
    assert "P1 judge walkthrough" not in html
    assert "Evidence chain</span><strong class=\"valid\">true" not in html


def test_demo_ui_private_service_error_names_401_403():
    request = demo_ui.httpx.Request("POST", "https://root.example/run_vendor_review")
    response = demo_ui.httpx.Response(403, json={"detail": "forbidden"}, request=request)
    exc = demo_ui.httpx.HTTPStatusError("forbidden", request=request, response=response)

    error = demo_ui._remote_error("Root Orchestrator", exc)

    assert error.title == "Private service returned 401/403"
    assert "HTTP 403" in error.detail
    assert "identity-token auth" in error.next_action
