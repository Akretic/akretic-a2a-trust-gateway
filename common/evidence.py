from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from common.models import Actor, now_iso
from common.paths import env_path

GENESIS_HASH = "0" * 64


def ledger_dir(path: str | Path | None = None) -> Path:
    if path is not None:
        target = Path(path)
    else:
        target = env_path("EVIDENCE_DIR", ".akretic/evidence")
    target.mkdir(parents=True, exist_ok=True)
    return target


def ledger_path(run_id: str, path: str | Path | None = None) -> Path:
    return ledger_dir(path) / f"{run_id}.jsonl"


def _gcs_bucket_name(path: str | Path | None = None) -> str | None:
    if path is not None:
        return None
    return os.getenv("AKRETIC_EVIDENCE_BUCKET") or os.getenv("EVIDENCE_GCS_BUCKET") or None


def _gcs_blob_name(run_id: str) -> str:
    prefix = (os.getenv("AKRETIC_EVIDENCE_PREFIX") or os.getenv("EVIDENCE_GCS_PREFIX", "evidence")).strip("/")
    return f"{prefix}/{run_id}.jsonl" if prefix else f"{run_id}.jsonl"


def _read_gcs_text(run_id: str, bucket_name: str) -> str:
    from google.api_core.exceptions import NotFound
    from google.cloud import storage

    client = storage.Client()
    blob = client.bucket(bucket_name).blob(_gcs_blob_name(run_id))
    try:
        return blob.download_as_text(encoding="utf-8")
    except NotFound:
        return ""


def _write_gcs_text(run_id: str, bucket_name: str, text: str) -> None:
    from google.cloud import storage

    client = storage.Client()
    blob = client.bucket(bucket_name).blob(_gcs_blob_name(run_id))
    blob.upload_from_string(text, content_type="application/jsonl")


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_event_hash(event: dict[str, Any]) -> str:
    material = {key: value for key, value in event.items() if key != "event_hash"}
    return hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()


def _last_hash(run_id: str, path: str | Path | None = None) -> str:
    bucket_name = _gcs_bucket_name(path)
    if bucket_name:
        events = read_events(run_id)
        return events[-1]["event_hash"] if events else GENESIS_HASH

    target = ledger_path(run_id, path)
    if not target.exists():
        return GENESIS_HASH
    last = None
    with target.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last = json.loads(line)
    return last["event_hash"] if last else GENESIS_HASH


def append_event(
    *,
    run_id: str,
    actor: Actor | dict[str, Any],
    agent_id: str,
    action: str,
    resource_id: str,
    outcome: str,
    reason: str,
    correlation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    path: str | Path | None = None,
) -> dict[str, Any]:
    actor_id = actor.actor_id if isinstance(actor, Actor) else actor.get("actor_id", "unknown")
    event_metadata = dict(metadata or {})
    event_metadata.setdefault("identity_source", "demo identity adapter")
    event_metadata.setdefault("browser_transport", "not used for server-side event")
    event_metadata.setdefault("verifier_transport", "server-side demo adapter")
    event_metadata.setdefault("transport", "server-side demo adapter")
    event = {
        "event_id": f"evt_{uuid4().hex}",
        "run_id": run_id,
        "actor_id": actor_id,
        "agent_id": agent_id,
        "action": action,
        "resource_id": resource_id,
        "outcome": outcome,
        "reason": reason,
        "correlation_id": correlation_id or f"corr_{uuid4().hex}",
        "prev_hash": _last_hash(run_id, path),
        "timestamp": now_iso(),
        "metadata": event_metadata,
    }
    event["event_hash"] = compute_event_hash(event)
    bucket_name = _gcs_bucket_name(path)
    line = json.dumps(event, sort_keys=True) + "\n"
    if bucket_name:
        existing = _read_gcs_text(run_id, bucket_name)
        _write_gcs_text(run_id, bucket_name, existing + line)
    else:
        target = ledger_path(run_id, path)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(line)
    return event


def read_events(run_id: str, path: str | Path | None = None) -> list[dict[str, Any]]:
    bucket_name = _gcs_bucket_name(path)
    if bucket_name:
        text = _read_gcs_text(run_id, bucket_name)
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    target = ledger_path(run_id, path)
    if not target.exists():
        return []
    with target.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def verify_chain(run_id: str, path: str | Path | None = None) -> dict[str, Any]:
    events = read_events(run_id, path)
    previous = GENESIS_HASH
    for index, event in enumerate(events):
        expected_hash = compute_event_hash(event)
        if event.get("prev_hash") != previous:
            return {
                "run_id": run_id,
                "valid": False,
                "event_count": len(events),
                "failed_index": index,
                "reason": "prev_hash mismatch",
            }
        if event.get("event_hash") != expected_hash:
            return {
                "run_id": run_id,
                "valid": False,
                "event_count": len(events),
                "failed_index": index,
                "reason": "event_hash mismatch",
            }
        previous = event["event_hash"]
    return {
        "run_id": run_id,
        "valid": True,
        "event_count": len(events),
        "head_hash": previous,
    }


def build_evidence_report(run_id: str, path: str | Path | None = None) -> dict[str, Any]:
    events = read_events(run_id, path)
    verification = verify_chain(run_id, path)
    a2a_calls = [event for event in events if event["action"] == "a2a_call"]
    retrieval_events = [event for event in events if event["action"] == "retrieve_internal"]
    knowledge_retrieval_events = [
        event for event in retrieval_events if event.get("agent_id") == "knowledge_agent"
    ]
    research_events = [event for event in events if event["action"] == "research_public"]
    model_events = [event for event in events if event["action"] == "summarize_review"]
    approval_events = [
        event
        for event in events
        if event["action"] in {"export_external", "request_approval", "approve_action"}
        or event["outcome"] == "approval_required"
    ]
    latest_model = {}
    if model_events:
        latest_metadata = model_events[-1].get("metadata", {})
        latest_model = {
            key: latest_metadata.get(key)
            for key in (
                "mode",
                "runtime_mode",
                "model",
                "service_path",
                "project_id",
                "location",
                "prompt_hash",
                "output_hash",
                "completion_hash",
                "guardrails",
                "permitted_source_ids",
                "denied_source_ids",
                "permitted_internal_source_ids",
                "permitted_public_source_ids",
                "model_context_source_ids",
                "model_context_source_ids_display",
                "restricted_canary_absent",
                "model_context_token_count",
                "policy_decision_ids",
                "retrieval_trace_id",
                "corpus_manifest_hash",
            )
            if latest_metadata.get(key) is not None
        }
    research_source_ids = sorted(
        {
            source_id
            for event in research_events
            for source_id in event.get("metadata", {}).get("source_ids", [])
        }
    )
    research_citations = sorted(
        {
            citation
            for event in research_events
            for citation in event.get("metadata", {}).get("citations", [])
        }
    )

    return {
        "run_id": run_id,
        "verification": verification,
        "summary": {
            "event_count": len(events),
            "a2a_call_count": len(a2a_calls),
            "policy_resource_ids": [
                event["resource_id"] for event in retrieval_events if event["agent_id"] == "policy_agent"
            ],
            "retrieval_allow_source_ids": [
                event["resource_id"]
                for event in knowledge_retrieval_events
                if event["outcome"] == "allow"
            ],
            "retrieval_deny_source_ids": [
                event["resource_id"]
                for event in knowledge_retrieval_events
                if event["outcome"] == "deny"
            ],
            "approval_required_actions": [
                event["action"] for event in approval_events if event["outcome"] == "approval_required"
            ],
            "research_event_count": len(research_events),
            "research_source_ids": research_source_ids,
            "research_citations": research_citations,
            "model_event_count": len(model_events),
            "model_modes": sorted(
                {
                    event.get("metadata", {}).get("mode")
                    for event in model_events
                    if event.get("metadata", {}).get("mode")
                }
            ),
            "latest_model": latest_model,
            "reviewer_decisions": [
                {
                    "resource_id": event["resource_id"],
                    "outcome": event["outcome"],
                    "actor_id": event["actor_id"],
                    "reviewer_id": event.get("metadata", {}).get("reviewer_id"),
                    "decided_at": event.get("metadata", {}).get("decided_at"),
                }
                for event in approval_events
                if event["action"] == "approve_action"
            ],
            "result_event_count": len([event for event in events if event["outcome"] == "result"]),
        },
        "a2a_calls": a2a_calls,
        "policy_decisions": [event for event in events if event["agent_id"] == "policy_agent"],
        "retrieval_events": retrieval_events,
        "research_events": research_events,
        "model_events": model_events,
        "approval_events": approval_events,
        "events": events,
    }
