from __future__ import annotations

from pathlib import Path
from typing import Any

from google.protobuf.json_format import ParseDict

from a2a.types import AgentCard

REQUIRED_CARD_FIELDS = {"name", "description", "version", "url", "skills"}
REQUIRED_A2A_SDK_FIELDS = {
    "supportedInterfaces",
    "securitySchemes",
    "defaultInputModes",
    "defaultOutputModes",
}


def validate_agent_card(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_CARD_FIELDS:
        if not card.get(field):
            errors.append(f"missing {field}")
    for field in REQUIRED_A2A_SDK_FIELDS:
        if not card.get(field):
            errors.append(f"missing {field}")
    if not isinstance(card.get("skills", []), list) or not card.get("skills"):
        errors.append("skills must be a non-empty list")
    for skill in card.get("skills", []):
        if not skill.get("id") or not skill.get("name") or not skill.get("description"):
            errors.append("each skill must include id, name, and description")
    try:
        ParseDict(card, AgentCard(), ignore_unknown_fields=True)
    except Exception as exc:  # pragma: no cover - exercised by SDK compatibility.
        errors.append(f"a2a-sdk validation failed: {exc}")
    return errors


def load_card(path: str | Path) -> dict[str, Any]:
    import json

    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)
