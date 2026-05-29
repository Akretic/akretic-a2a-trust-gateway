from pathlib import Path

from common.agent_cards import load_card, validate_agent_card


ROOT = Path(__file__).resolve().parents[1]


def test_agent_cards_are_valid_with_a2a_sdk_fields():
    for relative in [
        "agents/policy_agent/agent-card.json",
        "agents/knowledge_agent/agent-card.json",
        "agents/approval_evidence_agent/agent-card.json",
        "agents/research_agent/agent-card.json",
    ]:
        card = load_card(ROOT / relative)
        errors = validate_agent_card(card)
        assert errors == []
        skill_ids = {skill["id"] for skill in card["skills"]}
        assert skill_ids
        assert card["supportedInterfaces"][0]["url"] == card["url"]
        assert card["supportedInterfaces"][0]["protocolBinding"] == "HTTP+JSON"
        assert "demo-header" in card["securitySchemes"]
        assert card["defaultInputModes"] == ["application/json"]
        assert card["defaultOutputModes"] == ["application/json"]


def test_required_p0_skills_present():
    policy = load_card(ROOT / "agents/policy_agent/agent-card.json")
    knowledge = load_card(ROOT / "agents/knowledge_agent/agent-card.json")
    assert {"authorize_intent", "classify_resource", "explain_decision"}.issubset({s["id"] for s in policy["skills"]})
    assert {"retrieve_permitted_context", "list_sources", "redact_context"}.issubset({s["id"] for s in knowledge["skills"]})
