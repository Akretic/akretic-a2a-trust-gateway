from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from common.evidence import append_event
from common.models import Actor, Resource
from common.paths import env_path
from common.policy import ALLOW, evaluate


def load_metadata(metadata_path: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(metadata_path) if metadata_path else env_path("CORPUS_METADATA_PATH", "corpus/metadata.json")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)["documents"]


def read_document(doc: dict[str, Any], corpus_dir: str | Path | None = None) -> str:
    base = Path(corpus_dir) if corpus_dir else env_path("CORPUS_DIR", "corpus")
    return (base / doc["path"]).read_text(encoding="utf-8")


def _matches_query(query: str, text: str, doc: dict[str, Any]) -> bool:
    normalized = query.lower().strip()
    haystack = " ".join([
        text.lower(),
        doc.get("title", "").lower(),
        doc.get("source_id", "").lower(),
        doc.get("document_type", "").lower(),
    ])
    if not normalized:
        return True
    terms = [term for term in normalized.replace("-", " ").split() if len(term) > 2]
    return any(term in haystack for term in terms)


def retrieve_permitted_context(
    *,
    query: str,
    actor: Actor,
    run_id: str,
    max_chunks: int = 5,
    corpus_dir: str | Path | None = None,
    metadata_path: str | Path | None = None,
    evidence_path: str | Path | None = None,
    write_evidence: bool = False,
) -> dict[str, Any]:
    """Retrieve only chunks permitted before model context assembly."""
    correlation_id = f"corr_{uuid4().hex}"
    permitted_chunks: list[dict[str, Any]] = []
    denied_sources: list[dict[str, Any]] = []

    for doc in load_metadata(metadata_path):
        resource = Resource.from_dict(doc)
        decision = evaluate(
            actor=actor,
            action="retrieve_internal",
            resource=resource,
            run_id=run_id,
            context={"query": query, "correlation_id": correlation_id},
            correlation_id=correlation_id,
        )
        text = read_document(doc, corpus_dir)
        if decision.outcome == ALLOW and _matches_query(query, text, doc):
            permitted_chunks.append(
                {
                    "source_id": doc["source_id"],
                    "title": doc["title"],
                    "classification": doc["classification"],
                    "text": text,
                    "decision_id": decision.decision_id,
                }
            )
            if write_evidence:
                append_event(
                    run_id=run_id,
                    actor=actor,
                    agent_id="knowledge_agent",
                    action="retrieve_internal",
                    resource_id=doc["source_id"],
                    outcome="allow",
                    reason=decision.reason,
                    correlation_id=correlation_id,
                    path=evidence_path,
                    metadata={"decision_id": decision.decision_id},
                )
        elif decision.outcome != ALLOW:
            denied_sources.append(
                {
                    "source_id": doc["source_id"],
                    "classification": doc["classification"],
                    "reason": decision.reason,
                    "decision_id": decision.decision_id,
                }
            )
            if write_evidence:
                append_event(
                    run_id=run_id,
                    actor=actor,
                    agent_id="knowledge_agent",
                    action="retrieve_internal",
                    resource_id=doc["source_id"],
                    outcome="deny",
                    reason=decision.reason,
                    correlation_id=correlation_id,
                    path=evidence_path,
                    metadata={"decision_id": decision.decision_id},
                )

    return {
        "run_id": run_id,
        "actor_id": actor.actor_id,
        "query": query,
        "chunks": permitted_chunks[:max_chunks],
        "denied_sources": denied_sources,
        "correlation_id": correlation_id,
    }
