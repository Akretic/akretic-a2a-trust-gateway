from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI

app = FastAPI(title="Akretic Seeded Research Agent")
CARD_PATH = Path(__file__).resolve().parent / "agent-card.json"

SEEDED_SNIPPETS = [
    {
        "source_id": "public_seed_vendornova_001",
        "source_type": "synthetic_public",
        "title": "VendorNova public profile snippet",
        "text": "VendorNova is a synthetic SaaS automation vendor used for this challenge prototype.",
    },
    {
        "source_id": "public_seed_vendornova_002",
        "source_type": "synthetic_public",
        "title": "VendorNova public risk signal snippet",
        "text": "No seeded public breach signal is present in the synthetic corpus. Request additional evidence for encryption key rotation.",
    },
]


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "research-agent"}


@app.get("/agent-card.json")
@app.get("/.well-known/agent-card.json")
def agent_card() -> dict[str, Any]:
    return json.loads(CARD_PATH.read_text(encoding="utf-8"))


@app.post("/research_vendor_profile")
def research_vendor_profile(payload: dict[str, Any]) -> dict[str, Any]:
    return {"run_id": payload.get("run_id", "local-run"), "snippets": SEEDED_SNIPPETS[:1]}


@app.post("/check_public_risk_signals")
def check_public_risk_signals(payload: dict[str, Any]) -> dict[str, Any]:
    return {"run_id": payload.get("run_id", "local-run"), "snippets": SEEDED_SNIPPETS}
