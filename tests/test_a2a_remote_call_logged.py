from common.evidence import append_event, read_events
from common.identity import derive_actor


def test_a2a_remote_call_logged_with_correlation_id(tmp_path):
    actor = derive_actor("procurement_user")
    run_id = "test-a2a-call"
    event = append_event(
        run_id=run_id,
        actor=actor,
        agent_id="root_orchestrator",
        action="a2a_call",
        resource_id="akretic-policy-agent",
        outcome="result",
        reason="called remote A2A skill authorize_intent",
        correlation_id="corr-test-a2a",
        path=tmp_path,
        metadata={"caller": "root_orchestrator", "callee": "akretic-policy-agent", "skill": "authorize_intent"},
    )
    events = read_events(run_id, path=tmp_path)
    assert events[0]["event_hash"] == event["event_hash"]
    assert events[0]["correlation_id"] == "corr-test-a2a"
    assert events[0]["metadata"]["caller"] == "root_orchestrator"
    assert events[0]["metadata"]["callee"] == "akretic-policy-agent"
    assert events[0]["metadata"]["skill"] == "authorize_intent"
