from __future__ import annotations

from fastapi.testclient import TestClient

from demo_ui.main import app


def test_red_team_results_execute_all_cards_with_human_readable_fields():
    client = TestClient(app)

    response = client.get("/red-team/results.json")

    assert response.status_code == 200
    results = response.json()["results"]
    assert {result["challenge"] for result in results} == {
        "self_assert_admin",
        "executive_memo",
        "retrieve_all",
        "prompt_injection_export",
        "approve_as_procurement",
        "knowledge_without_receipt",
        "unauthorized_evidence",
        "tamper_evidence",
    }
    assert all("expected_outcome" in result for result in results)
    assert all("actual_outcome" in result for result in results)
    assert all("persona" in result for result in results)
    assert all("policy_decision" in result for result in results)
    assert all(result["pass"] is True for result in results)


def test_executive_memo_red_team_page_is_human_readable_denial():
    client = TestClient(app)

    response = client.post("/red-team/run", data={"challenge": "executive_memo"})

    assert response.status_code == 200
    html = response.text
    assert "Red-Team Challenge Result" in html
    assert "executive_acquisition_memo" in html
    assert "denied before model" in html.lower()
    assert "restricted_canary_absent" in html
