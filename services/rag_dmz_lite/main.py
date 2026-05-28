from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header

from common.identity import derive_actor_from_request
from common.rag import load_metadata, retrieve_permitted_context

app = FastAPI(title="Akretic RAG DMZ-lite / Knowledge Agent")
CARD_PATH = Path(__file__).resolve().parents[2] / "agents" / "knowledge_agent" / "agent-card.json"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "rag-dmz-lite"}


@app.get("/agent-card.json")
@app.get("/.well-known/agent-card.json")
def agent_card() -> dict[str, Any]:
    return json.loads(CARD_PATH.read_text(encoding="utf-8"))


@app.post("/retrieve_permitted_context")
def retrieve(payload: dict[str, Any], x_akretic_persona: str | None = Header(default=None)) -> dict[str, Any]:
    actor = derive_actor_from_request(demo_persona=x_akretic_persona or payload.get("persona"), body_claims=payload.get("actor"))
    return retrieve_permitted_context(
        query=payload.get("query", ""),
        actor=actor,
        run_id=payload.get("run_id", "local-run"),
        max_chunks=int(payload.get("max_chunks", 5)),
        write_evidence=bool(payload.get("write_evidence", True)),
    )


@app.post("/list_sources")
def list_sources(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    docs = load_metadata()
    return {"sources": [{k: doc[k] for k in ["source_id", "title", "classification", "allowed_groups"]} for doc in docs]}


@app.post("/redact_context")
def redact_context(payload: dict[str, Any]) -> dict[str, Any]:
    chunks = payload.get("chunks", [])
    return {"chunks": chunks, "note": "P0 control is pre-context filtering; this endpoint is for minimization of already permitted chunks."}
