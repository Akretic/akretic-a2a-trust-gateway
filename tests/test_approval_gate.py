import pytest
import httpx

from agents.approval_evidence_agent.main import app as approval_app
from common.evidence import read_events
from common.approval import ApprovalStore
from common.identity import derive_actor
from common.models import Resource
from tests.service_utils import run_service


def test_approval_gate_blocks_until_reviewer_decision():
    store = ApprovalStore()
    requester = derive_actor("procurement_user")
    reviewer = derive_actor("security_reviewer")
    resource = Resource(
        resource_id="vendornova_exception_export",
        classification="internal",
        source_type="draft",
        allowed_groups=("procurement_user",),
        external_release_allowed=False,
    )

    approval = store.create(
        actor=requester,
        action="export_external",
        resource=resource,
        run_id="test-approval",
        draft_payload="Synthetic exception draft for VendorNova.",
    )
    assert approval.status == "pending"

    with pytest.raises(PermissionError):
        store.decide(
            approval_id=approval.approval_id,
            reviewer=derive_actor("procurement_user"),
            status="approved",
            reason="self approval should fail",
        )

    decided = store.decide(
        approval_id=approval.approval_id,
        reviewer=reviewer,
        status="approved",
        reason="approved for demo",
    )
    assert decided.status == "approved"
    assert decided.reviewer_id == reviewer.actor_id


def test_approval_service_records_request_and_reviewer_decision(monkeypatch, tmp_path):
    run_id = "test-approval-service"
    monkeypatch.setenv("EVIDENCE_DIR", str(tmp_path))
    resource = {
        "resource_id": "vendornova_exception_export",
        "classification": "internal",
        "source_type": "draft",
        "allowed_groups": ["procurement_user"],
        "external_release_allowed": False,
    }

    with run_service(approval_app) as approval_url:
        request_response = httpx.post(
            f"{approval_url}/request_approval",
            json={
                "run_id": run_id,
                "persona": "procurement_user",
                "action": "export_external",
                "resource": resource,
                "draft_payload": "Synthetic exception draft for VendorNova.",
            },
            headers={"x-akretic-persona": "procurement_user"},
            timeout=5.0,
        )
        request_response.raise_for_status()
        approval = request_response.json()

        self_approval = httpx.post(
            f"{approval_url}/decide_approval",
            json={"approval_id": approval["approval_id"], "status": "approved"},
            headers={"x-akretic-persona": "procurement_user"},
            timeout=5.0,
        )
        assert self_approval.status_code == 403

        decision_response = httpx.post(
            f"{approval_url}/decide_approval",
            json={
                "approval_id": approval["approval_id"],
                "status": "approved",
                "reason": "approved for demo",
            },
            headers={"x-akretic-persona": "security_reviewer"},
            timeout=5.0,
        )
        decision_response.raise_for_status()
        decision = decision_response.json()

    events = read_events(run_id, path=tmp_path)
    approval_events = {event["action"]: event for event in events}
    assert approval["status"] == "pending"
    assert decision["status"] == "approved"
    assert approval_events["request_approval"]["outcome"] == "approval_required"
    assert approval_events["approve_action"]["outcome"] == "approved"
