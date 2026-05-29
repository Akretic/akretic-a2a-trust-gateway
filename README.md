# Akretic A2A Trust Gateway

## What it is

Akretic A2A Trust Gateway is a Track 3 challenge prototype: a trust gateway/control
plane for A2A enterprise agents. It demonstrates one VendorNova vendor-risk review
where agents collaborate, but the model cannot decide what it may read, share,
approve, or export.

## Who buys it

The target buyer is a procurement, security, legal, or AI platform team that wants
agent workflows to use enterprise context without losing authorization, approval,
and evidence boundaries.

## Why now

Multi-agent workflows can move internal context across tools and agents faster
than traditional access review can inspect. This prototype shows policy before
model context, approval before sensitive side effects, and tamper-evident evidence
for the run.

## Live demo

- Public Cloud Run demo: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
- Hosted demo video: `https://youtu.be/FAziZQFkIfw`
- Unlisted Akretic page: `https://akretic.com/a2a-trust-gateway-demo`
- Repository: `https://github.com/Akretic/akretic-a2a-trust-gateway`

## 90-second proof path

1. Open the public Cloud Run URL and confirm the page labels the build as a
   challenge prototype using synthetic data.
2. Start the VendorNova review as `procurement_user`.
3. Confirm Vertex/Gemini mode is visible, then scan the proof row:
   Identity -> Policy -> RAG Filter -> A2A -> Approval -> Evidence Verify.
4. Confirm permitted sources are listed and
   `Denied before model context: executive_acquisition_memo.` is visible.
5. Confirm the external action returns `approval_required` and remains blocked
   until a reviewer records approve/reject.
6. Confirm the A2A table shows Agent Card URL, agent, skill/intent,
   caller/callee, `correlation_id`, outcome, and evidence event/hash.
7. Confirm evidence verification reports a valid hash chain and event count.

## Track 3 alignment

The proof path runs on Google Cloud Run, uses Vertex AI Gemini for permitted
context summarization, exposes A2A Agent Cards and skill-call evidence, and uses
a Google ADK Workflow wrapper that delegates to the verified root orchestrator.
Gate0-lite policy, RAG DMZ-lite filtering, approval state, and evidence
verification remain outside Gemini.

## A2A and ADK proof

- Agent Cards validate against the `a2a-sdk` package and remain available at
  `/agent-card.json` and `/.well-known/agent-card.json`.
- A2A call evidence records caller, callee, skill/intent, Agent Card URL,
  `correlation_id`, evidence event ID, and event hash.
- The root endpoint enters a `google-adk` Workflow wrapper that delegates to
  `run_vendor_review_workflow`; the wrapper does not authorize, retrieve,
  approve, or verify evidence itself.
- See `docs/a2a_intent_map.md` and `docs/adk_alignment.md`.

## Evidence report

The sample evidence report shows policy decisions, retrieval allow/deny events,
A2A calls, approval state, reviewer decision, model path metadata, and hash-chain
verification for a synthetic VendorNova run.

## Limitations

This is a challenge prototype. It is not a production launch approval, legal
opinion, compliance certification, Marketplace listing, or universal data-leak
prevention guarantee. It uses synthetic data only and proves one narrow
workflow.

P0, P1, P2, P3, P4, P5, and P6 are cleared. The hosted demo video URL is recorded,
the final submission package is rebuilt, and the challenge-readiness remediation
audit has restored submission-ready status for the declared prototype scope. Coding agents
must read `PROJECT_SOURCE_OF_TRUTH.md` and then `docs/priority_ladder.md` before
selecting work so remediation follow-up does not jeopardize the accepted package
and P7 productization work does not displace the challenge path.

## Fast start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

On Windows, if `python` points to Python 3.14, create the virtualenv with Python 3.12
or 3.13 instead because the pinned FastAPI/Pydantic stack targets Python 3.11-3.13:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Run one service locally:

```bash
uvicorn services.gate0_lite.main:app --reload --port 8101
```

Smoke the local policy service:

```bash
curl -s http://127.0.0.1:8101/.well-known/agent-card.json
curl -s -X POST http://127.0.0.1:8101/authorize_intent \
  -H "content-type: application/json" \
  -H "x-akretic-persona: procurement_user" \
  -d '{"action":"retrieve_internal","resource":{"resource_id":"vendornova_profile","classification":"public","source_type":"synthetic","allowed_groups":["procurement_user"]}}'
```

Run the local service stack:

```bash
bash scripts/run_local.sh
```

## Important files for Codex

- `AGENTS.md` — repo-level instructions Codex must read before work.
- `PROJECT_SOURCE_OF_TRUTH.md` — locked scope and product invariants.
- `docs/priority_ladder.md` — P0-P7 priority ladder; P0-P6 and final challenge-readiness remediation are complete.
- `docs/adk_alignment.md` — P6 ADK concept mapping and wrapper boundary.
- `docs/a2a_intent_map.md` — explicit A2A protocol proof table.
- `docs/third_party_rights.md` and `docs/eligibility_statement.md` — public-safe rights and original-work notes.
- `docs/public_release_gate.md` — scan gate before making the GitHub repo public.
- `docs/challenge_readiness_remediation.md` — final remediation summary and AuditOps evidence map.
- `docs/p1_acceptance.md` — completed P1 demo-path polish acceptance checks.
- `docs/p2_acceptance.md` — completed P2 Gemini/Vertex hardening acceptance checks.
- `docs/p3_acceptance.md` — completed P3 Cloud Run deployment hardening acceptance checks.
- `docs/p4_acceptance.md` — completed P4 judge hardening acceptance checks.
- `docs/p5_acceptance.md` — completed P5 submission package acceptance checks.
- `docs/p6_acceptance.md` — P6 ADK alignment merge bar.
- `docs/devpost_answers.md` — paste-ready public submission answers.
- `docs/demo_video_script.md` and `docs/video_shot_list.md` — hosted demo video planning material.
- `docs/judge_readiness.md` — public judge-path checklist and trust-boundary verifier.
- `docs/cloudrun_runbook.md` — Cloud Run verification, troubleshooting, and rollback drill commands.
- `CODEX_TASKS.md` — bounded `/goal` prompts and ticket sequence.
- `GOOGLE_TOOLS.md` — required and stretch Google Cloud tools.
- `DAILY_BUILD_TEMPO.md` — day-by-day shipping cadence.
- `ACCEPTANCE_CRITERIA.md` — P0 tests and proof artifacts.
- `docs/deployment.md` — Cloud Run deployment boundaries and commands.
- `docs/deployment_notes.md` — current Cloud Run resources and smoke proof.

## Current implementation status

This packet includes:

- deterministic policy evaluator skeleton;
- demo identity adapter that ignores request-body privilege claims;
- metadata-filtered synthetic corpus retrieval;
- hash-chained JSONL evidence ledger;
- approval request and reviewer decision path for export-style side effects;
- structured evidence report with A2A, retrieval, approval, reviewer decision, and verify sections;
- FastAPI service shells for the agents and core services;
- Agent Card JSON for each remote agent;
- root-to-Policy and root-to-Knowledge HTTP A2A calls with evidence logging;
- root summarization adapter for Vertex AI Gemini, with a labeled local test mode;
- baseline P0 tests;
- Cloud Run deployment scaffolding and authenticated Cloud Run smoke proof.

Current Cloud Run note: the demo services deploy, the public UI path passes,
and private agent services remain behind Cloud Run IAM.

The root Gemini path is isolated behind `common/gemini.py`. Set `AKRETIC_GEMINI_MODE=vertex`
with `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `VERTEX_MODEL` for the Cloud Run demo.
The `local` mode is explicitly labeled and reserved for tests.

## 90-second judge walkthrough

Target demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

1. Open the public Cloud Run demo URL and confirm the page labels the build as a challenge prototype using synthetic data.
2. Keep persona as `procurement_user`, keep the VendorNova query, and select `Start VendorNova Review`.
3. On the review page, scan the proof row: Identity, Policy, RAG Filter, A2A, Approval, Evidence Verify.
4. Confirm the model panel says `Mode: vertex`, `Model: gemini-2.5-flash`, project `akretic-a2a-trust-gateway`, and location `us-central1`.
5. Confirm the page shows `run_id`, permitted source IDs, and `Denied before model context: executive_acquisition_memo.`
6. Confirm the external/sensitive action is `approval_required` and the export result is blocked pending reviewer action.
7. Scan A2A Proof for Agent Card URL, agent, skill/intent, caller/callee,
   `correlation_id`, outcome, and evidence event/hash.
8. Record an approve or reject decision as `security_reviewer`.
9. Confirm Evidence Verification reports a valid hash chain and event count.

## Gemini/Vertex behavior

In Cloud Run, the root orchestrator uses Vertex AI Gemini through the thin adapter
in `common/gemini.py` with:

```text
AKRETIC_GEMINI_MODE=vertex
GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
```

Gemini summarizes only permitted synthetic context after identity derivation,
Gate0-lite policy decisions, RAG DMZ-lite filtering, and approval gating have
already run. Gemini does not decide identity, tenant, role, group membership,
authorization, retrieval access, approval state, external export completion, or
evidence validity. Denied source IDs can appear as proof, but denied source text
is filtered before prompt assembly and must not appear in model input, UI output,
logs, or evidence reports. Local mode is explicitly labeled and reserved for
tests or local development.

## What this proves

- A root workflow can coordinate specialized agents over A2A Agent Cards and skill calls.
- Identity is derived from the demo request header, not upgraded by request-body claims.
- Gate0-lite policy checks run before retrieval and before sensitive external action completion.
- RAG DMZ-lite filters restricted synthetic chunks before model context is assembled.
- The VendorNova executive memo is denied before model context while permitted sources are still summarized.
- External/sensitive action completion is approval-gated.
- Evidence events are hash-chained and can be verified for this synthetic run.

## What this does not claim

- This is not a production launch approval or compliance certification.
- This is not a legal opinion, audit attestation, or Marketplace status claim.
- This is not a guarantee that every possible data leak or policy bypass is impossible.
- This does not replace enterprise SSO, full policy administration, monitoring, incident response, or customer-specific controls.
- The current proof path uses Vertex/Gemini summarization, A2A Agent Card skill-call wiring, and a Google ADK Workflow wrapper that delegates to the verified orchestrator path without overclaiming Agent Runtime or Agent Registry integration.

## P6 ADK alignment posture

The current proof path runs on Cloud Run with Vertex/Gemini summarization,
A2A Agent Card skill-call wiring, and a Google ADK Workflow wrapper around the
verified orchestrator path. Authorization, retrieval filtering, approvals, and
evidence remain outside Gemini and are not delegated to the model.

This does not claim Agent Runtime, Agent Registry, or a replacement public demo
path. See `docs/adk_alignment.md`.

## Judging instructions

Target demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

The intended judging flow:

1. Open the demo URL.
2. Keep persona as `procurement_user`.
3. Start the VendorNova review.
4. Confirm the page shows a `run_id`, permitted sources, denied sources, an
   `approval_required` external-action decision, and hash-chain verification.
5. Submit the reviewer decision as `security_reviewer`.
6. Use the sample evidence report in `artifacts/` or the private evidence report
   endpoint to inspect the A2A, policy, retrieval, approval, and verification events.

The public UI uses Cloud Run's no-invoker IAM check mode so it can remain public
for judging without an `allUsers` IAM binding. Verify the public proof path with:

```powershell
.\scripts\verify_judge_readiness.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

## Public-claim discipline

Use: policy-mediated, permission-preserving for this synthetic corpus, approval-gated, tamper-evident, challenge prototype.

Do not make claims of perfect security, compliance guarantees, universal leak prevention, legal attestation, Marketplace status, certification, or production launch readiness.
