from __future__ import annotations

import asyncio
import socket
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import httpx
import uvicorn

from agents.root_orchestrator.main import run_vendor_review_workflow
from common.evidence import read_events
from services.gate0_lite.main import app as policy_app
from services.rag_dmz_lite.main import app as knowledge_app


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@contextmanager
def _run_service(app: Any) -> Iterator[str]:
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base_url}/healthz", timeout=1.0)
            if response.status_code == 200:
                break
        except httpx.HTTPError:
            pass
        time.sleep(0.05)
    else:
        server.should_exit = True
        thread.join(timeout=5)
        raise RuntimeError(f"service did not start at {base_url}")

    try:
        yield base_url
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def test_root_calls_policy_and_knowledge_agents_over_a2a(monkeypatch, tmp_path):
    run_id = "test-a2a-root"
    monkeypatch.setenv("EVIDENCE_DIR", str(tmp_path))

    with _run_service(policy_app) as policy_url:
        with _run_service(knowledge_app) as knowledge_url:
            monkeypatch.setenv("POLICY_AGENT_URL", policy_url)
            monkeypatch.setenv("KNOWLEDGE_AGENT_URL", knowledge_url)
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
    assert all(event["correlation_id"].startswith("corr_") for event in a2a_events)
    assert all(event["metadata"]["caller"] == "root_orchestrator" for event in a2a_events)
    assert all(
        event["metadata"]["identity_source"] == "x-akretic-persona header"
        for event in a2a_events
    )
    assert {"allow", "approval_required"}.issubset({event["outcome"] for event in policy_events})
