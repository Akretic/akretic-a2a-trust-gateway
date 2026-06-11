# Akretic A2A Trust Gateway — Starter Packet

This repository is the starting implementation packet for the Akretic A2A Trust Gateway challenge prototype.
It is intentionally narrow: one vendor-risk review workflow that proves policy-mediated multi-agent collaboration.

## Product thesis

Enterprise agents should collaborate over A2A without letting the model decide what it may read, call, send, or approve.

## P0 proof chain

The demo must prove these controls in one short path:

1. Root orchestrator creates a `run_id` for a VendorNova review.
2. Policy Agent evaluates each material intent before retrieval, research, A2A exchange, approval, export, or verification.
3. RAG DMZ-lite filters synthetic corpus chunks by derived user identity before model context is assembled.
4. Research Agent returns seeded allowlisted VendorNova public snippets with source IDs and citations.
5. External-facing or sensitive side effects return `approval_required` and pause until reviewer action.
6. Evidence ledger records allow, deny, research, approval, A2A call, and result events in a hash chain.
7. `/verify/{run_id}` proves the chain is intact and detects tampering behind a demo viewer role check.

P0, P1, P2, P3, P4, and P5 are cleared. The hosted demo video URL is recorded,
the final submission package is rebuilt, and P6 ADK alignment exploration may
continue in isolated branches. Coding agents
must read `PROJECT_SOURCE_OF_TRUTH.md` and then `docs/priority_ladder.md` before
selecting work so P6 exploration does not jeopardize the P5 accepted package
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

Local mode is the default. It is intentionally labeled and uses deterministic
summaries for local development and tests:

```bash
AKRETIC_RUNTIME_MODE=local
```

Cloud judge mode must be explicit and must use Vertex/Gemini. It fails safe if
the Vertex configuration is missing instead of falling back to local summaries.

## Important files for Codex

- `AGENTS.md` — repo-level instructions Codex must read before work.
- `PROJECT_SOURCE_OF_TRUTH.md` — locked scope and product invariants.
- `docs/priority_ladder.md` — P0-P7 priority ladder; P5 is complete and P6 ADK alignment exploration may continue in isolated branches.
- `docs/adk_alignment.md` — P6 ADK concept mapping and wrapper boundary.
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
- `corpus/documents/*.md` and `corpus/metadata.json` as the synthetic enterprise corpus source of truth;
- Cloud Storage corpus loading when `AKRETIC_CORPUS_BACKEND=gcs` and `AKRETIC_RUNTIME_MODE=cloud`;
- `/corpus/status`, `/corpus`, and `/corpus/metadata.json` for corpus backend, manifest, metadata, and persona access proof;
- `/playground` for guided chips and free-form reviewer prompts mapped to governed intents;
- hash-chained JSONL evidence ledger;
- approval request and reviewer decision path for export-style side effects;
- structured evidence report with A2A, retrieval, approval, reviewer decision, and verify sections;
- model context envelope and A2A Trust Receipt endpoints for current-run proof artifacts;
- current-run evidence report links from the run page, including downloadable JSON for that exact `run_id`;
- FastAPI service shells for the agents and core services;
- Agent Card JSON for each remote agent;
- root-to-Policy, Knowledge, Research, and Approval/Evidence HTTP A2A calls with evidence logging;
- A2A evidence metadata with HTTP status, latency, request hash, and response hash;
- root summarization adapter for Vertex AI Gemini, with a labeled local test mode;
- model events with runtime mode, prompt hash, and output/completion hash;
- evidence/verify UI routes with demo viewer role checks;
- `scripts/make_final_handoff.py` for final verifier output, raw responses, screenshots, manifest, and zip packaging;
- baseline P0 tests;
- Cloud Run deployment scaffolding and authenticated Cloud Run smoke proof.

Current Cloud Run note: the demo services deploy, the public UI path passes,
and private agent services remain behind Cloud Run IAM.

The root Gemini path is isolated behind `common/gemini.py`. Set
`AKRETIC_RUNTIME_MODE=cloud` with `GOOGLE_CLOUD_PROJECT`,
`GOOGLE_CLOUD_LOCATION`, and `VERTEX_MODEL` for the Cloud Run demo. Cloud mode
requires Vertex/Gemini and does not silently fall back to local deterministic
summaries. The `local` runtime mode is explicitly labeled and reserved for tests
or local development.

## Corpus and playground proof

The demo is backed by a synthetic enterprise corpus under `corpus/documents/`
with document metadata in `corpus/metadata.json`. The metadata includes source
ID, title, classification, source type, document type, allowed groups, release
flag, sensitivity tags, vendor ID, creation timestamp, content hash, storage
URI, and index status. No customer data, private third-party data, real secrets,
or production enterprise data is used.

Local mode loads the corpus from the repository. Cloud mode must set:

```text
AKRETIC_RUNTIME_MODE=cloud
AKRETIC_CORPUS_BACKEND=gcs
AKRETIC_CORPUS_BUCKET=<bucket>
AKRETIC_CORPUS_PREFIX=<prefix>
AKRETIC_EVIDENCE_BUCKET=<bucket>
```

The free-form `/playground` maps reviewer prompts to constrained governed
intents. Prompt chips are examples, not the only supported path. Unknown or
unsafe prompts return `unsupported_intent` or a governed denial/fallback. Gemini
sees only permitted model context assembled after identity derivation,
Gate0-lite policy, Knowledge Agent filtering, seeded/allowlisted public
research, and approval gating.

The `/corpus` explorer shows what synthetic documents exist and evaluates the
current persona's metadata/content/model-context access per document. Restricted
content is withheld when policy denies access; denial source IDs can appear as
proof but denied document text is not used as the control.

## Public Demo URL

Public demo URL placeholder: `https://<PUBLIC_DEMO_URL>`

Replace the placeholder with the active Cloud Run demo UI URL when preparing the
final judge packet.

## 1-2 minute final recording path

Target demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

Before recording, run the warmup command in the Cloud Run verification section or open the footer link labeled `Warm demo services`. Keep min instances enabled during judging.

Testing personas:

- `procurement_user`: starts the VendorNova review and is denied executive-only source text before model context.
- `security_reviewer`: records the approval decision and can inspect evidence and trust receipts.
- `admin`: alternate evidence-review persona for verifier and handoff checks.

1. Open the public Cloud Run demo URL.
2. Click `Start VendorNova Review` and show the immediate governed progress overlay.
3. On the review result page, scan the proof chips: Cloud Run, Vertex Gemini, A2A Agent Cards resolved, restricted memo denied before Gemini, export gate `approval_required`, and hash chain valid.
4. Open `/playground` and run `Can I see the executive acquisition memo?`; confirm `Denied before model` and `Request governed: executive_acquisition_memo denied`.
5. Return to the guided run and try the approval form as `procurement_user`; confirm the unauthorized decision is not recorded.
6. Record an approve or reject decision as `security_reviewer`.
7. Open the current-run evidence report for that exact `run_id`.
8. Open the A2A Trust Receipt and confirm the Agent Card URLs, event hashes, final head hash, model context envelope, and approval/evidence trail.

## Gemini/Vertex behavior

In Cloud Run, the root orchestrator uses Vertex AI Gemini through the thin adapter
in `common/gemini.py` with:

```text
AKRETIC_RUNTIME_MODE=cloud
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

- A root workflow can coordinate specialized agents over the A2A-style Agent Card and skill-call path.
- Identity is derived from the demo request header, not upgraded by request-body claims.
- Gate0-lite policy checks run before retrieval and before sensitive external action completion.
- RAG DMZ-lite filters restricted synthetic chunks before model context is assembled.
- The VendorNova executive memo is denied before model context while permitted sources are still summarized.
- External/sensitive action completion is approval-gated.
- Authorized reviewer decisions are recorded; no external egress is performed in this challenge prototype.
- Evidence events are hash-chained and can be verified for this synthetic run.

## What this does not claim

- This is not a production launch approval or compliance certification.
- This is not a legal opinion, audit attestation, or Marketplace status claim.
- This is not a guarantee that every possible data leak or policy bypass is impossible.
- This does not replace enterprise SSO, full policy administration, monitoring, incident response, or customer-specific controls.
- The current proof path uses Vertex/Gemini summarization and thin A2A Agent Card skill-call wiring, with ADK alignment documented as part of the Google Cloud agent architecture path rather than overclaiming full ADK-native orchestration.

## P6 ADK alignment posture

The current proof path runs on Cloud Run with Vertex/Gemini summarization and
thin A2A Agent Card skill-call wiring. P6 adds ADK alignment documentation and
an ADK-compatible wrapper around the verified orchestrator path. Authorization,
retrieval filtering, approvals, and evidence remain outside Gemini and are not
delegated to the model.

This does not claim full ADK-native orchestration, Agent Runtime, Agent Registry,
or a replacement public demo path. See `docs/adk_alignment.md`.

## Judging instructions

Target demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

The intended judging flow:

1. Open the demo URL.
2. Keep persona as `procurement_user`.
3. Start the VendorNova review.
4. Confirm the page shows a `run_id`, permitted sources, denied sources, an
   `approval_required` external-action decision, and hash-chain verification.
5. Submit the reviewer decision as `security_reviewer`.
6. Use the current-run evidence link on the run page to inspect the A2A, policy,
   research, retrieval, model, approval, and verification events for that exact `run_id`.

The public UI uses Cloud Run's no-invoker IAM check mode so it can remain public
for judging without an `allUsers` IAM binding. Verify the public proof path with:

For Bash or Git Bash:

```bash
export DEMO_URL="https://<PUBLIC_DEMO_URL>"
export ROOT_URL="https://<ROOT_SERVICE_URL>"
export POLICY_URL="https://<POLICY_SERVICE_URL>"
export KNOWLEDGE_URL="https://<KNOWLEDGE_SERVICE_URL>"
export RESEARCH_URL="https://<RESEARCH_SERVICE_URL>"
export APPROVAL_URL="https://<APPROVAL_EVIDENCE_SERVICE_URL>"
export PROJECT_LABEL="<PROJECT_OR_REDACTED_PROJECT_LABEL>"
export DEMO_UI_REVISION="<DEMO_UI_REVISION>"
export ROOT_REVISION="<ROOT_REVISION>"
export POLICY_REVISION="<POLICY_REVISION>"
export KNOWLEDGE_REVISION="<KNOWLEDGE_REVISION>"
export RESEARCH_REVISION="<RESEARCH_REVISION>"
export APPROVAL_REVISION="<APPROVAL_REVISION>"
export AKRETIC_CLOUD_RUN_AUTH=identity_token

.venv/Scripts/python.exe scripts/warmup_cloud_demo.py --base-url "$DEMO_URL"
.venv/Scripts/python.exe scripts/p0_verify.py --base-url "$DEMO_URL" --mode cloud --root-url "$ROOT_URL" --policy-url "$POLICY_URL" --knowledge-url "$KNOWLEDGE_URL" --research-url "$RESEARCH_URL" --approval-url "$APPROVAL_URL" --expect-vertex --fail-on-local
.venv/Scripts/python.exe scripts/p0_verify.py --base-url "$DEMO_URL" --mode cloud --root-url "$ROOT_URL" --policy-url "$POLICY_URL" --knowledge-url "$KNOWLEDGE_URL" --research-url "$RESEARCH_URL" --approval-url "$APPROVAL_URL" --expect-vertex --fail-on-local --expect-corpus-backend gcs --expect-freeform-playground --expect-corpus-explorer --expect-corpus-live-retrieval --expect-decision-receipts --expect-trust-receipt --expect-model-context-envelope --expect-red-team-cards
.venv/Scripts/python.exe scripts/make_final_handoff.py --mode cloud --base-url "$DEMO_URL" --root-url "$ROOT_URL" --policy-url "$POLICY_URL" --knowledge-url "$KNOWLEDGE_URL" --research-url "$RESEARCH_URL" --approval-url "$APPROVAL_URL" --project-label "$PROJECT_LABEL" --demo-ui-revision "$DEMO_UI_REVISION" --root-revision "$ROOT_REVISION" --policy-revision "$POLICY_REVISION" --knowledge-revision "$KNOWLEDGE_REVISION" --research-revision "$RESEARCH_REVISION" --approval-revision "$APPROVAL_REVISION"
powershell.exe -ExecutionPolicy Bypass -File scripts/verify_judge_readiness.ps1
powershell.exe -ExecutionPolicy Bypass -File scripts/verify_cloudrun_p0.ps1 -RequirePublic
```

For PowerShell:

```powershell
$env:AKRETIC_CLOUD_RUN_AUTH = "identity_token"
$DemoUrl = "https://<PUBLIC_DEMO_URL>"
$RootUrl = "https://<ROOT_SERVICE_URL>"
$PolicyUrl = "https://<POLICY_SERVICE_URL>"
$KnowledgeUrl = "https://<KNOWLEDGE_SERVICE_URL>"
$ResearchUrl = "https://<RESEARCH_SERVICE_URL>"
$ApprovalUrl = "https://<APPROVAL_EVIDENCE_SERVICE_URL>"
$ProjectLabel = "<PROJECT_OR_REDACTED_PROJECT_LABEL>"
$DemoUiRevision = "<DEMO_UI_REVISION>"
$RootRevision = "<ROOT_REVISION>"
$PolicyRevision = "<POLICY_REVISION>"
$KnowledgeRevision = "<KNOWLEDGE_REVISION>"
$ResearchRevision = "<RESEARCH_REVISION>"
$ApprovalRevision = "<APPROVAL_REVISION>"

.\.venv\Scripts\python.exe scripts\warmup_cloud_demo.py --base-url $DemoUrl
.\.venv\Scripts\python.exe scripts\p0_verify.py --base-url $DemoUrl --mode cloud --root-url $RootUrl --policy-url $PolicyUrl --knowledge-url $KnowledgeUrl --research-url $ResearchUrl --approval-url $ApprovalUrl --expect-vertex --fail-on-local
.\.venv\Scripts\python.exe scripts\p0_verify.py --base-url $DemoUrl --mode cloud --root-url $RootUrl --policy-url $PolicyUrl --knowledge-url $KnowledgeUrl --research-url $ResearchUrl --approval-url $ApprovalUrl --expect-vertex --fail-on-local --expect-corpus-backend gcs --expect-freeform-playground --expect-corpus-explorer --expect-corpus-live-retrieval --expect-decision-receipts --expect-trust-receipt --expect-model-context-envelope --expect-red-team-cards
.\.venv\Scripts\python.exe scripts\make_final_handoff.py --mode cloud --base-url $DemoUrl --root-url $RootUrl --policy-url $PolicyUrl --knowledge-url $KnowledgeUrl --research-url $ResearchUrl --approval-url $ApprovalUrl --project-label $ProjectLabel --demo-ui-revision $DemoUiRevision --root-revision $RootRevision --policy-revision $PolicyRevision --knowledge-revision $KnowledgeRevision --research-revision $ResearchRevision --approval-revision $ApprovalRevision
.\scripts\verify_judge_readiness.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

If a real impersonation service account is required for private-service checks,
set `AKRETIC_CLOUD_RUN_IMPERSONATE_SERVICE_ACCOUNT` before running either
command block.

For local rehearsal:

```powershell
.\.venv\Scripts\python.exe scripts\p0_verify.py --base-url http://127.0.0.1:8081 --mode local
.\.venv\Scripts\python.exe scripts\p0_verify.py --base-url http://127.0.0.1:8081 --mode local --expect-corpus-backend local --expect-freeform-playground --expect-corpus-explorer --expect-corpus-live-retrieval --expect-decision-receipts --expect-trust-receipt --expect-model-context-envelope --expect-red-team-cards
```

## Public-claim discipline

Use: policy-mediated, permission-preserving for this synthetic corpus, approval-gated, tamper-evident, challenge prototype.

Do not make claims of perfect security, compliance guarantees, universal leak prevention, legal attestation, Marketplace status, certification, or production launch readiness.
