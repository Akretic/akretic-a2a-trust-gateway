from __future__ import annotations

import os
from typing import Any

from common.models import Actor

LOCAL_TEST_MODE = "local"
VERTEX_MODE = "vertex"


def build_vendor_review_prompt(
    *,
    query: str,
    actor: Actor,
    retrieval: dict[str, Any],
    export_decision: dict[str, Any],
) -> dict[str, Any]:
    permitted_chunks = retrieval.get("chunks", [])
    permitted_source_ids = [chunk["source_id"] for chunk in permitted_chunks]
    denied_source_ids = [source["source_id"] for source in retrieval.get("denied_sources", [])]

    context_blocks = []
    for chunk in permitted_chunks:
        context_blocks.append(
            "\n".join(
                [
                    f"source_id: {chunk['source_id']}",
                    f"title: {chunk['title']}",
                    f"classification: {chunk['classification']}",
                    "text:",
                    chunk["text"],
                ]
            )
        )

    system_instruction = (
        "You are the Akretic A2A Trust Gateway root summarizer. "
        "Use only the permitted context provided in the prompt. "
        "Do not infer, summarize, reveal, or quote denied source contents. "
        "Authorization, approval, identity, and evidence decisions are already made outside the model."
    )
    contents = "\n\n".join(
        [
            "Vendor-risk review target: VendorNova",
            f"Requester query: {query}",
            f"Derived actor: {actor.actor_id} role={actor.role} groups={', '.join(actor.groups)}",
            f"Permitted source IDs: {', '.join(permitted_source_ids) or 'none'}",
            f"Denied source IDs withheld from context: {', '.join(denied_source_ids) or 'none'}",
            f"External export policy outcome: {export_decision['outcome']}",
            "Permitted context:",
            "\n\n---\n\n".join(context_blocks) if context_blocks else "No permitted context returned.",
            (
                "Return a concise VendorNova review summary with source IDs, open evidence gaps, "
                "and the current approval/export status."
            ),
        ]
    )

    return {
        "system_instruction": system_instruction,
        "contents": contents,
        "permitted_source_ids": permitted_source_ids,
        "denied_source_ids": denied_source_ids,
    }


def _local_summary(prompt: dict[str, Any], export_decision: dict[str, Any]) -> str:
    sources = ", ".join(prompt["permitted_source_ids"]) or "none"
    return (
        "LOCAL_DETERMINISTIC_SUMMARY_FOR_TESTS_ONLY: "
        "VendorNova review assembled from permitted synthetic context only. "
        f"Permitted sources: {sources}. "
        f"External export decision: {export_decision['outcome']}."
    )


def _vertex_summary(
    *,
    prompt: dict[str, Any],
    project_id: str,
    location: str,
    model: str,
) -> str:
    from google import genai
    from google.genai.types import GenerateContentConfig, HttpOptions

    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
        http_options=HttpOptions(api_version="v1"),
    )
    response = client.models.generate_content(
        model=model,
        contents=prompt["contents"],
        config=GenerateContentConfig(
            system_instruction=prompt["system_instruction"],
            temperature=0.2,
            max_output_tokens=512,
        ),
    )
    return response.text or ""


def summarize_vendor_review(
    *,
    query: str,
    actor: Actor,
    retrieval: dict[str, Any],
    export_decision: dict[str, Any],
    mode: str | None = None,
) -> dict[str, Any]:
    prompt = build_vendor_review_prompt(
        query=query,
        actor=actor,
        retrieval=retrieval,
        export_decision=export_decision,
    )
    mode = mode or os.getenv("AKRETIC_GEMINI_MODE", LOCAL_TEST_MODE)
    model = os.getenv("VERTEX_MODEL", "gemini-2.5-flash")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID", "")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    if mode == LOCAL_TEST_MODE:
        text = _local_summary(prompt, export_decision)
        return {
            "mode": mode,
            "model": "local-deterministic-test-summary",
            "text": text,
            "prompt": prompt,
            "service_path": "local deterministic summary for tests only",
        }

    if mode != VERTEX_MODE:
        raise ValueError(f"Unknown Gemini mode: {mode}")
    if not project_id:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT or PROJECT_ID is required for Vertex Gemini mode")

    text = _vertex_summary(
        prompt=prompt,
        project_id=project_id,
        location=location,
        model=model,
    )
    return {
        "mode": mode,
        "model": model,
        "text": text,
        "prompt": prompt,
        "service_path": "Vertex AI Gemini via google-genai",
        "project_id": project_id,
        "location": location,
    }
