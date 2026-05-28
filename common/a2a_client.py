from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx

from common.evidence import append_event
from common.models import Actor


async def fetch_agent_card(base_url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{base_url.rstrip('/')}/.well-known/agent-card.json")
        response.raise_for_status()
        return response.json()


async def call_skill(
    *,
    base_url: str,
    skill: str,
    payload: dict[str, Any],
    run_id: str,
    caller_agent_id: str,
    actor: Actor,
    evidence_path: str | None = None,
) -> dict[str, Any]:
    correlation_id = payload.get("correlation_id") or f"corr_{uuid4().hex}"
    payload = {**payload, "run_id": run_id, "correlation_id": correlation_id}
    async with httpx.AsyncClient(timeout=20.0) as client:
        card = await fetch_agent_card(base_url)
        response = await client.post(f"{base_url.rstrip('/')}/{skill}", json=payload)
        response.raise_for_status()
        result = response.json()
    append_event(
        run_id=run_id,
        actor=actor,
        agent_id=caller_agent_id,
        action="a2a_call",
        resource_id=card.get("name", base_url),
        outcome="result",
        reason=f"called remote A2A skill {skill}",
        correlation_id=correlation_id,
        path=evidence_path,
        metadata={"callee": card.get("name"), "skill": skill, "base_url": base_url},
    )
    return result
