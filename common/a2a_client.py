from __future__ import annotations

import os
import hashlib
import json
import subprocess
import time
from typing import Any
from uuid import uuid4

import httpx

from common.evidence import append_event
from common.models import Actor


def _stable_hash(value: Any) -> str:
    material = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _auth_headers(base_url: str, headers: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(headers or {})
    if os.getenv("AKRETIC_CLOUD_RUN_AUTH") != "identity_token":
        return merged

    from google.auth.transport.requests import Request
    from google.oauth2 import id_token

    audience = base_url.rstrip("/")
    try:
        token = id_token.fetch_id_token(Request(), audience)
    except Exception:
        token = _gcloud_identity_token(audience)
    merged["Authorization"] = f"Bearer {token}"
    return merged


def cloud_run_auth_headers(base_url: str, headers: dict[str, str] | None = None) -> dict[str, str]:
    return _auth_headers(base_url, headers)


def _gcloud_identity_token(audience: str) -> str:
    gcloud = "gcloud.cmd" if os.name == "nt" else "gcloud"
    impersonate = (
        os.getenv("AKRETIC_CLOUD_RUN_IMPERSONATE_SERVICE_ACCOUNT")
        or os.getenv("GOOGLE_IMPERSONATE_SERVICE_ACCOUNT")
        or ""
    ).strip()
    commands: list[list[str]] = []
    if impersonate:
        commands.append(
            [
                gcloud,
                "auth",
                "print-identity-token",
                f"--impersonate-service-account={impersonate}",
                f"--audiences={audience}",
                "--include-email",
            ]
        )
    commands.append([gcloud, "auth", "print-identity-token", f"--audiences={audience}"])
    commands.append([gcloud, "auth", "print-identity-token"])

    errors: list[str] = []
    for command in commands:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=30)
        token = completed.stdout.strip()
        if completed.returncode == 0 and token:
            return token
        errors.append((completed.stderr or completed.stdout or "no output").strip())
    raise RuntimeError("unable to mint Cloud Run identity token with gcloud: " + " | ".join(errors))


async def fetch_agent_card(base_url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{base_url.rstrip('/')}/.well-known/agent-card.json",
            headers=_auth_headers(base_url, headers),
        )
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
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    correlation_id = payload.get("correlation_id") or f"corr_{uuid4().hex}"
    payload = {**payload, "run_id": run_id, "correlation_id": correlation_id}
    request_hash = _stable_hash({"skill": skill, "payload": payload})
    agent_card_url = f"{base_url.rstrip('/')}/.well-known/agent-card.json"
    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=20.0) as client:
        request_headers = _auth_headers(base_url, headers)
        card = await fetch_agent_card(base_url, headers=headers)
        response = await client.post(
            f"{base_url.rstrip('/')}/{skill}",
            json=payload,
            headers=request_headers,
        )
        http_status = response.status_code
        response.raise_for_status()
        result = response.json()
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    response_hash = _stable_hash(result)
    event = append_event(
        run_id=run_id,
        actor=actor,
        agent_id=caller_agent_id,
        action="a2a_call",
        resource_id=card.get("name", base_url),
        outcome="result",
        reason=f"called remote A2A skill {skill}",
        correlation_id=correlation_id,
        path=evidence_path,
        metadata={
            "caller": caller_agent_id,
            "callee": card.get("name"),
            "skill": skill,
            "base_url": base_url,
            "agent_card_url": agent_card_url,
            "advertised_url": card.get("url"),
            "http_status": http_status,
            "latency_ms": latency_ms,
            "policy_decision_id": payload.get("policy_decision_id"),
            "decision_receipt_id": (
                payload.get("policy_decision_receipt") or payload.get("decision_receipt") or {}
            ).get("decision_id"),
            "request_hash": request_hash,
            "response_hash": response_hash,
            "identity_source": "demo identity adapter",
            "browser_transport": "not used for server-side A2A call",
            "verifier_transport": "x-akretic-persona header",
            "transport": "x-akretic-persona header",
        },
    )
    return {
        **result,
        "_a2a_event": {
            "event_id": event["event_id"],
            "event_hash": event["event_hash"],
            "agent_card_url": agent_card_url,
            "base_url": base_url,
            "caller": caller_agent_id,
            "callee": card.get("name"),
            "skill": skill,
            "correlation_id": correlation_id,
            "outcome": event["outcome"],
            "http_status": http_status,
            "latency_ms": latency_ms,
            "request_hash": request_hash,
            "response_hash": response_hash,
        },
    }
