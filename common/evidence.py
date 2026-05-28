from __future__ import annotations

import hashlib
import json
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


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_event_hash(event: dict[str, Any]) -> str:
    material = {key: value for key, value in event.items() if key != "event_hash"}
    return hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()


def _last_hash(run_id: str, path: str | Path | None = None) -> str:
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
        "metadata": metadata or {},
    }
    event["event_hash"] = compute_event_hash(event)
    target = ledger_path(run_id, path)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def read_events(run_id: str, path: str | Path | None = None) -> list[dict[str, Any]]:
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
