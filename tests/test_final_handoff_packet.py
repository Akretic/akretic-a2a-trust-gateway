from __future__ import annotations

from scripts.make_final_handoff import (
    _capture_screenshots_from_artifacts,
    _validate_cloud_manifest,
    scan_forbidden_strings,
    validate_primary_run_integrity,
)


def test_cloud_packet_scan_flags_local_strings(tmp_path):
    clean = tmp_path / "clean.txt"
    dirty = tmp_path / "dirty.txt"
    clean.write_text("Cloud Run Vertex proof", encoding="utf-8")
    dirty.write_text("http://localhost:8081 should not be in a cloud packet", encoding="utf-8")

    findings = scan_forbidden_strings(tmp_path, mode="cloud")

    assert findings == [{"path": str(dirty), "token": "localhost"}]


def test_cloud_packet_scan_flags_sample_evidence_and_unknown_model_fields(tmp_path):
    sample = tmp_path / "sample.txt"
    unknown = tmp_path / "unknown.txt"
    service_unknown = tmp_path / "service.txt"
    sample.write_text("sample evidence report should not ship", encoding="utf-8")
    unknown.write_text("Model: UNKNOWN", encoding="utf-8")
    service_unknown.write_text("Cloud Run service URL: UNKNOWN", encoding="utf-8")

    findings = scan_forbidden_strings(tmp_path, mode="cloud")

    assert {"path": str(sample), "token": "sample evidence"} in findings
    assert any(
        finding["path"] == str(unknown) and finding["token"] == "UNKNOWN"
        for finding in findings
    )
    assert any(
        finding["path"] == str(service_unknown) and finding["token"] == "UNKNOWN"
        for finding in findings
    )


def test_local_packet_scan_allows_local_strings(tmp_path):
    dirty = tmp_path / "dirty.txt"
    dirty.write_text("http://127.0.0.1:8081 is allowed in local rehearsal packets", encoding="utf-8")

    assert scan_forbidden_strings(tmp_path, mode="local") == []


def test_primary_run_integrity_accepts_single_judge_run(tmp_path):
    judge_run_id = "run_primary123"
    raw = tmp_path / "raw"
    raw.mkdir()
    for relative in (
        "run.html",
        "evidence-unauthorized.json",
        "evidence-before-decision.json",
        "evidence-before-decision.html",
        "approval-unauthorized.html",
        "approval-authorized.html",
        "model-context-envelope.json",
        "model-context-envelope.html",
        "a2a-trust-receipt.json",
        "a2a-trust-receipt.html",
        "evidence-final.json",
        "evidence-final.html",
        "verify-final.json",
    ):
        (raw / relative).write_text(f"review artifact for {judge_run_id}", encoding="utf-8")

    assert validate_primary_run_integrity(tmp_path, judge_run_id) == []


def test_primary_run_integrity_fails_on_mixed_run_ids(tmp_path):
    judge_run_id = "run_primary123"
    raw = tmp_path / "raw"
    raw.mkdir()
    for relative in (
        "run.html",
        "evidence-unauthorized.json",
        "evidence-before-decision.json",
        "evidence-before-decision.html",
        "approval-unauthorized.html",
        "approval-authorized.html",
        "model-context-envelope.json",
        "model-context-envelope.html",
        "a2a-trust-receipt.json",
        "a2a-trust-receipt.html",
        "evidence-final.json",
        "evidence-final.html",
        "verify-final.json",
    ):
        text = f"review artifact for {judge_run_id}"
        if relative == "evidence-final.json":
            text += " plus run_other456"
        (raw / relative).write_text(text, encoding="utf-8")

    failures = validate_primary_run_integrity(tmp_path, judge_run_id)

    assert failures == [
        {
            "path": "raw/evidence-final.json",
            "reason": "mixed run IDs",
            "run_ids": ["run_other456"],
        }
    ]


def test_screenshot_manifest_paths_are_packet_relative(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    for name in (
        "home.html",
        "run.html",
        "evidence-before-decision.html",
        "approval-unauthorized.html",
        "approval-authorized.html",
        "evidence-final.html",
    ):
        (raw / name).write_text("<main>run_primary123</main>", encoding="utf-8")
    (raw / "evidence-unauthorized.json").write_text(
        '{"run_id":"run_primary123","status_code":403}', encoding="utf-8"
    )

    screenshots = _capture_screenshots_from_artifacts(tmp_path, 10_000)

    assert screenshots["home"] == "screenshots/home.png"
    assert screenshots["evidence_unauthorized"] == "screenshots/07-evidence-unauthorized.png"
    assert all("\\" not in value for key, value in screenshots.items() if key != "source")
    assert all(not value.startswith(str(tmp_path)) for key, value in screenshots.items() if key != "source")


def test_cloud_manifest_requires_public_agent_cards_and_identity_fields():
    base_manifest = {
        "packet_type": "cloud_judge_proof",
        "runtime_mode": "cloud",
        "model_mode": "vertex",
        "model": "gemini-2.5-flash",
        "project_label": "akretic-a2a-trust-gateway",
        "location": "us-central1",
        "commit_sha": "abc123",
        "corpus_backend": "gcs",
        "corpus_manifest_hash": "f" * 64,
        "corpus_document_count": 9,
        "warmup_output": "warmup-output.json",
        "readiness_burnin_output": "readiness-burnin-output.json",
        "deploy_manifest": "deploy-manifest.json",
        "image_digest": "sha256:" + "a" * 64,
        "build_id": "build-123",
        "identity_source": "demo identity adapter",
        "browser_transport": "viewer persona selector",
        "verifier_transport": "x-akretic-persona header",
        "cloud_run_service_urls": {
            "demo_ui": "https://demo.example",
            "root": "https://root.example",
            "policy": "https://policy.example",
            "knowledge": "https://knowledge.example",
            "research": "https://research.example",
            "approval": "https://approval.example",
        },
        "cloud_run_revisions": {
            "demo_ui": "demo-00001-abc",
            "root": "root-00001-abc",
            "policy": "policy-00001-abc",
            "knowledge": "knowledge-00001-abc",
            "research": "research-00001-abc",
            "approval": "approval-00001-abc",
        },
        "a2a_agent_card_urls": {
            "policy": "https://policy.example/.well-known/agent-card.json",
            "knowledge": "https://knowledge.example/.well-known/agent-card.json",
            "research": "https://research.example/.well-known/agent-card.json",
            "approval": "https://approval.example/.well-known/agent-card.json",
        },
        "min_instances": {
            "akretic-demo-ui": 1,
            "akretic-root-orchestrator": 1,
            "akretic-policy-agent": 1,
            "akretic-knowledge-agent": 1,
            "akretic-research-agent": 1,
            "akretic-approval-evidence": 1,
        },
    }

    _validate_cloud_manifest(base_manifest)

    bad = {**base_manifest, "a2a_agent_card_urls": {"policy": "http://127.0.0.1:8101/.well-known/agent-card.json"}}
    try:
        _validate_cloud_manifest(bad)
    except RuntimeError as exc:
        assert "Agent Card URL" in str(exc)
    else:
        raise AssertionError("expected local Agent Card URL to fail cloud manifest validation")
