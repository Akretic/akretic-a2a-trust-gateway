# Priority Ladder

This file is the repository-readable priority ladder for choosing post-P0 work.
Coding agents must read `PROJECT_SOURCE_OF_TRUTH.md` first, then this file,
before selecting or expanding work.

## Current Lane

- P0 is cleared.
- P1 demo-path polish is the active lane.
- P6 is blocked non-blocking Google stretch until P1-P5 are stable.
- P7 is blocked post-challenge productization until P1-P5 are stable and the challenge path is complete.
- P1 acceptance is tracked in `docs/p1_acceptance.md`.

## Ladder

| Priority | Lane | Status | Scope boundary |
|---|---|---|---|
| P0 | Local trust proof chain | Cleared | Identity derivation, Gate0-lite decisions, RAG DMZ-lite pre-context filtering, A2A calls, approval gate, evidence ledger, and public-claims guardrails are proven for the VendorNova demo. |
| P1 | Demo-path polish | Active | Tighten the existing judge/demo path without changing core architecture: UI clarity, repeatability, error handling, docs, runbook quality, and demo evidence visibility. |
| P2 | Gemini/Vertex integration | Implemented; hardening planned | Improve the approved Vertex AI Gemini path while preserving Gate0-lite as the policy decision point and keeping denied content out of model context. |
| P3 | Cloud Run deployment | Implemented; hardening planned | Harden deploy scripts, service configuration, IAM notes, verification scripts, and rollback/runbook material for the existing Cloud Run shape. |
| P4 | Judge hardening | Planned | Make the public judging path more resilient and self-explanatory while keeping admin/evidence surfaces role-checked and claims bounded. |
| P5 | Submission package | Planned | Keep submission artifacts, screenshots, evidence samples, architecture images, and public-safe copy current with the running demo. |
| P6 | Google stretch | Blocked; non-blocking stretch | Explore ADK alignment, Agent Runtime or Registry, Firestore, Vertex AI embeddings, and controlled Google Search grounding only after P1-P5 are stable. |
| P7 | Post-challenge productization | Blocked; post-challenge | Consider SSO, real enterprise connectors, broader policy administration, production monitoring, incident workflows, and customer environment hardening only after P1-P5 are stable and the challenge path is complete. |

## Selection Rules

1. Do not pick P6 or P7 work if any P1-P5 acceptance gap is open.
2. Do not let Gemini, ADK, embeddings, or search grounding decide authorization.
3. Do not introduce customer data, private third-party data, real secrets, or production certification claims.
4. Do not expand the workflow beyond VendorNova unless the source of truth is updated first.
5. Prefer narrow branches named after the active priority, for example `p1/demo-path-polish`.
