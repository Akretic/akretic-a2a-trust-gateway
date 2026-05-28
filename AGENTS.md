# AGENTS.md — Akretic A2A Trust Gateway

This file is the operating contract for Codex agents working in this repository.

## Mission

Build a narrow P0 challenge prototype: Akretic A2A Trust Gateway for B2B vendor-risk review.
The system must show that enterprise agents can collaborate over A2A while authorization, retrieval filtering, approvals, and evidence stay outside the model.

## Required reading order

Before selecting work, read `PROJECT_SOURCE_OF_TRUTH.md`, then
`docs/priority_ladder.md`. The source of truth defines product boundaries; the
priority ladder defines the current post-P0 lane and prevents stretch work from
displacing active priorities.

## Non-negotiable architecture

- Demo UI: FastAPI/server-rendered HTML or minimal SPA.
- Root Orchestrator: ADK/Gemini via Vertex AI path after deterministic controls are stable.
- Policy Agent / Gate0-lite: deterministic Python/YAML policy evaluator.
- Knowledge Agent / RAG DMZ-lite: filters synthetic corpus by derived identity before any model context.
- Research Agent: seeded or allowlisted public snippets only for P0.
- Approval/Evidence Agent: approval state machine and hash-chained evidence ledger.
- Runtime: Cloud Run first. Agent Runtime, Agent Registry, Firestore, embeddings, and Google Search grounding are stretch only.

## Development rules

1. Build only the assigned priority-ladder lane or explicitly assigned feature. Do not expand scope.
2. Do not rename the product or alter the core workflow without updating `PROJECT_SOURCE_OF_TRUTH.md`.
3. Do not add a new framework unless the current task explicitly requires it.
4. Every externally visible route or tool call must show where identity comes from.
5. Request-body claims must never upgrade tenant, role, or group membership.
6. Every material retrieval, research call, A2A call, approval action, export action, and verify/report action must have a Gate0-lite decision where applicable.
7. Every material allow, deny, approval_required, approval decision, A2A call, and result must write an evidence event.
8. Retrieval features must filter restricted chunks before model context is assembled. Do not implement post-generation redaction as the main control.
9. Side-effect features must return `approval_required` before execution when policy requires review.
10. Demo-critical paths must call real local/remote services. If a stub is used, label it explicitly and record the stub/service path in evidence.
11. Use synthetic data only. Do not add customer data, private third-party data, or real secrets.
12. Public-facing copy must use the language in `docs/submission_answers_public.md` and avoid overclaims.

## Definition of done for any Codex change

- Code is implemented in the existing structure.
- Unit or integration tests are added or updated.
- `pytest -q` passes locally unless a blocker is documented.
- A short summary lists changed files, tests run, and remaining risks.
- If behavior is user-visible, README or docs are updated.
- If the feature changes policy, retrieval, approval, identity, A2A, or evidence semantics, update `ACCEPTANCE_CRITERIA.md` or `PROJECT_SOURCE_OF_TRUTH.md`.

## Commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
bash scripts/run_local.sh
```

## Default task prompt

Build only the P0 feature assigned. Preserve the Akretic A2A Trust Gateway architecture. For any route or tool call, include derived identity, Gate0-lite decision where applicable, evidence event write, and tests. If the feature touches retrieval, restricted chunks must be filtered before model context. If it touches side effects, return `approval_required` before execution. Do not add product scope.
