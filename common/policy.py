from __future__ import annotations

from typing import Any
from uuid import uuid4

import yaml

from common.models import Actor, PolicyDecision, Resource
from common.paths import env_path

ALLOW = "allow"
DENY = "deny"
APPROVAL_REQUIRED = "approval_required"


def load_policy(path: str | None = None) -> dict[str, Any]:
    policy_path = env_path("POLICY_PATH", path or "policies/policy.yaml")
    with policy_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _group_intersection(actor: Actor, resource: Resource) -> bool:
    return bool(set(actor.groups).intersection(set(resource.allowed_groups)))


def evaluate(
    *,
    actor: Actor,
    action: str,
    resource: Resource,
    run_id: str = "local-run",
    context: dict[str, Any] | None = None,
    policy_path: str | None = None,
    correlation_id: str | None = None,
) -> PolicyDecision:
    """Deterministic P0 policy evaluator.

    The evaluator is deliberately simple for the challenge prototype. It is not an LLM prompt.
    """
    policy = load_policy(policy_path)
    context = context or {}
    correlation_id = correlation_id or context.get("correlation_id") or f"corr_{uuid4().hex}"

    if action == "retrieve_internal":
        if resource.classification == "public":
            return PolicyDecision.create(
                run_id=run_id,
                actor=actor,
                action=action,
                resource=resource,
                outcome=ALLOW,
                reason="public resource allowed for demo retrieval",
                correlation_id=correlation_id,
            )
        if _group_intersection(actor, resource):
            return PolicyDecision.create(
                run_id=run_id,
                actor=actor,
                action=action,
                resource=resource,
                outcome=ALLOW,
                reason="actor group is permitted by resource metadata",
                correlation_id=correlation_id,
            )
        return PolicyDecision.create(
            run_id=run_id,
            actor=actor,
            action=action,
            resource=resource,
            outcome=DENY,
            reason="actor group is not permitted by resource metadata",
            correlation_id=correlation_id,
        )

    if action == "research_public":
        if resource.source_type in {"synthetic_public", "allowlisted_public", "public"} or resource.classification == "public":
            return PolicyDecision.create(
                run_id=run_id,
                actor=actor,
                action=action,
                resource=resource,
                outcome=ALLOW,
                reason="public research source is seeded or allowlisted",
                correlation_id=correlation_id,
            )
        return PolicyDecision.create(
            run_id=run_id,
            actor=actor,
            action=action,
            resource=resource,
            outcome=DENY,
            reason="public research source is not allowlisted",
            correlation_id=correlation_id,
        )

    if action in set(policy.get("sensitive_side_effects", [])):
        required_role = policy.get("approval_roles", {}).get(action, "security_reviewer")
        return PolicyDecision.create(
            run_id=run_id,
            actor=actor,
            action=action,
            resource=resource,
            outcome=APPROVAL_REQUIRED,
            reason="sensitive or external-facing side effect requires reviewer approval",
            required_approval_role=required_role,
            correlation_id=correlation_id,
        )

    if action in set(policy.get("admin_actions", [])):
        allowed_roles = set(policy.get("admin_action_roles", {}).get(action, ["admin"]))
        if actor.role in allowed_roles or set(actor.groups).intersection(allowed_roles):
            return PolicyDecision.create(
                run_id=run_id,
                actor=actor,
                action=action,
                resource=resource,
                outcome=ALLOW,
                reason="evidence action permitted for demo reviewer/admin persona",
                correlation_id=correlation_id,
            )
        return PolicyDecision.create(
            run_id=run_id,
            actor=actor,
            action=action,
            resource=resource,
            outcome=DENY,
            reason="evidence action requires demo reviewer/admin persona",
            correlation_id=correlation_id,
        )

    if action in {"list_sources", "classify_resource", "explain_decision"}:
        return PolicyDecision.create(
            run_id=run_id,
            actor=actor,
            action=action,
            resource=resource,
            outcome=ALLOW,
            reason="read-only support action allowed",
            correlation_id=correlation_id,
        )

    return PolicyDecision.create(
        run_id=run_id,
        actor=actor,
        action=action,
        resource=resource,
        outcome=DENY,
        reason="default deny for unknown action",
        correlation_id=correlation_id,
    )
