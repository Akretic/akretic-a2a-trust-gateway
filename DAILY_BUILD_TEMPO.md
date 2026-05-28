# Daily Build Tempo

This tempo assumes an 8-day build window. Compress by merging adjacent days only after the current day’s done condition is green.

## Day 0 — Control setup

**Objective:** Create repo, install dependencies, confirm Codex operating rules, create Google project.

Morning:
- Initialize Git repo.
- Commit starter packet.
- Open Codex app/CLI at repo root.
- Confirm Codex reads `AGENTS.md`.

Afternoon:
- Create Google Cloud project.
- Enable required APIs.
- Create Artifact Registry repository.
- Create `.env.local` from `.env.example`.

Done when:
- `pytest -q` passes locally.
- `PROJECT_ID` and `REGION` are set.
- First clean commit exists.

## Day 1 — Deterministic control plane

**Objective:** Identity, policy, corpus, and evidence are testable before any model integration.

Build:
- Gate0-lite allow/deny/approval_required.
- Demo identity adapter that ignores request-body privilege claims.
- Synthetic corpus and metadata.
- Evidence event hash chain.

Done when:
- `test_identity_spoofing.py`, `test_policy_decisions.py`, and `test_evidence_verify.py` pass.

## Day 2 — RAG DMZ-lite and service shells

**Objective:** Retrieval filter proves restricted chunks never reach context.

Build:
- Metadata-filtered retrieval.
- Knowledge Agent API.
- Policy Agent API.
- Denied retrieval evidence.

Done when:
- Allowed VendorNova retrieval succeeds.
- Executive memo retrieval is denied before context.
- `test_rag_filtering.py` passes.

## Day 3 — A2A minimum

**Objective:** A2A is real enough for the demo.

Build:
- Policy Agent Card.
- Knowledge Agent Card.
- Root HTTP A2A adapter.
- A2A evidence event for caller/callee/skill/correlation_id.

Done when:
- Agent Cards are reachable locally.
- Root calls Policy and Knowledge agents over HTTP adapter.
- `test_a2a_cards.py` and remote-call logging test pass.

## Day 4 — ADK/Gemini root orchestrator

**Objective:** Gemini summarizes permitted context only.

Build:
- ADK root agent or thin root service that wraps ADK where stable.
- Vertex AI/Gemini path.
- Prompt restricting model to authorized context.
- Source IDs in final review.

Done when:
- VendorNova summary uses permitted source IDs.
- Denied executive memo content is absent from prompt/context/output.

## Day 5 — Approval and evidence report

**Objective:** Sensitive action pause is visible.

Build:
- Approval request creation.
- Approve/reject reviewer endpoints.
- Export/draft side-effect gate.
- Evidence report and `/verify/{run_id}`.

Done when:
- Draft/export returns `approval_required`.
- Action cannot complete before approval.
- Evidence report shows allow, deny, approval_required, approval decision, and result.

## Day 6 — Cloud Run deployment

**Objective:** Public demo URL works.

Build:
- Container/deploy scripts.
- Cloud Run services.
- Env configuration.
- Cloud Logging run_id fields.

Done when:
- Public URL runs full demo path.
- Logs show run_id across services.
- Redeploy command is documented.

## Day 7 — Hardening and claim discipline

**Objective:** Remove fragile paths and unsupported claims.

Build:
- Fix all P0 tests.
- Remove hidden stubs from the green demo path.
- Add explicit limitation notes where needed.
- Run public claims check.

Done when:
- `pytest -q` passes.
- No public copy says unhackable, guaranteed compliance, production-ready, Marketplace-approved, legal non-repudiation, or universal data-leak prevention.

## Day 8 — Submission package

**Objective:** Ship judge-ready artifacts.

Build:
- 1–2 minute video.
- README judging instructions.
- Public brief/PDF.
- Architecture screenshot.
- Evidence sample.
- Devpost answers.

Done when:
- Demo URL stays accessible.
- Video shows product actually functioning.
- Submission copy matches implemented features.
