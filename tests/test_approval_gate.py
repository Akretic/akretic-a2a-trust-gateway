import pytest

from common.approval import ApprovalStore
from common.identity import derive_actor
from common.models import Resource


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
