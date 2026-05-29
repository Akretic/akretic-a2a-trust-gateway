# Priority Ladder

This file is the repository-readable priority ladder for choosing post-P0 work.
Coding agents must read `PROJECT_SOURCE_OF_TRUTH.md` first, then this file,
before selecting or expanding work.

## Current Lane

- P0 is cleared.
- P1 demo-path polish is complete.
- P2 Gemini/Vertex integration hardening is complete.
- P3 Cloud Run deployment hardening is complete.
- P4 Judge hardening is complete.
- P5 submission package is complete.
- Hosted demo video URL is recorded.
- Unlisted Akretic landing page is live at `https://akretic.com/a2a-trust-gateway-demo`.
- P6 ADK alignment hardening is complete.
- P7 remains post-challenge productization and must not displace the challenge path.
- P1 acceptance is tracked in `docs/p1_acceptance.md`.
- P2 acceptance is tracked in `docs/p2_acceptance.md`.
- P3 acceptance is tracked in `docs/p3_acceptance.md`.
- P4 acceptance is tracked in `docs/p4_acceptance.md`.
- P5 acceptance is tracked in `docs/p5_acceptance.md`.
- P6 acceptance is tracked in `docs/p6_acceptance.md`.

## Ladder

| Priority | Lane | Status | Scope boundary |
|---|---|---|---|
| P0 | Local trust proof chain | Cleared | Identity derivation, Gate0-lite decisions, RAG DMZ-lite pre-context filtering, A2A calls, approval gate, evidence ledger, and public-claims guardrails are proven for the VendorNova demo. |
| P1 | Demo-path polish | Complete | Tighten the existing judge/demo path without changing core architecture: UI clarity, repeatability, error handling, docs, runbook quality, and demo evidence visibility. |
| P2 | Gemini/Vertex integration | Complete | Improve the approved Vertex AI Gemini path while preserving Gate0-lite as the policy decision point and keeping denied content out of model context. |
| P3 | Cloud Run deployment | Complete | Harden deploy scripts, service configuration, IAM notes, verification scripts, and rollback/runbook material for the existing Cloud Run shape. |
| P4 | Judge hardening | Complete | Make the public judging path more resilient and self-explanatory while keeping admin/evidence surfaces role-checked and claims bounded. |
| P5 | Submission package | Complete | Final package, hosted video URL, public-safe brief, screenshots, sample evidence report, and submission docs are prepared and verified. |
| P6 | ADK alignment hardening | Complete | Strengthen the ADK story without replacing the working proof path. Prefer an ADK-compatible root wrapper that delegates to the verified orchestrator, docs mapping current root behavior to ADK concepts, and tests proving Gate0-lite, RAG DMZ-lite, approval, and evidence are not bypassed. Do not prioritize Firestore, embeddings, search grounding, Agent Runtime, or Registry. |
| P7 | Post-challenge productization | Post-challenge | Consider SSO, real enterprise connectors, broader policy administration, production monitoring, incident workflows, and customer environment hardening only after the challenge path is complete. |

## Selection Rules

1. P6 work must stay in isolated branches and must not jeopardize the P5 accepted package.
2. Do not pick P7 work until post-challenge productization is explicitly assigned.
3. Do not let Gemini, future ADK-aligned orchestration, embeddings, or search grounding decide authorization.
4. Do not introduce customer data, private third-party data, real secrets, or production certification claims.
5. Do not expand the workflow beyond VendorNova unless the source of truth is updated first.
6. Prefer narrow branches named after the active priority, for example `p6/adk-alignment`.
