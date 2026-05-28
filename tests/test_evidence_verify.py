import json

from common.evidence import append_event, ledger_path, verify_chain
from common.identity import derive_actor


def test_evidence_hash_chain_valid_and_tamper_detected(tmp_path):
    actor = derive_actor("procurement_user")
    run_id = "test-evidence"
    append_event(
        run_id=run_id,
        actor=actor,
        agent_id="policy_agent",
        action="retrieve_internal",
        resource_id="vendornova_profile",
        outcome="allow",
        reason="test allow",
        path=tmp_path,
    )
    append_event(
        run_id=run_id,
        actor=actor,
        agent_id="knowledge_agent",
        action="retrieve_internal",
        resource_id="vendornova_profile",
        outcome="result",
        reason="test result",
        path=tmp_path,
    )

    valid = verify_chain(run_id, path=tmp_path)
    assert valid["valid"] is True
    assert valid["event_count"] == 2

    target = ledger_path(run_id, path=tmp_path)
    lines = target.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["outcome"] = "deny"
    lines[0] = json.dumps(first, sort_keys=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    tampered = verify_chain(run_id, path=tmp_path)
    assert tampered["valid"] is False
    assert tampered["reason"] == "event_hash mismatch"
