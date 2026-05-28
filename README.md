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
4. External-facing or sensitive side effects return `approval_required` and pause until reviewer action.
5. Evidence ledger records allow, deny, approval, A2A call, and result events in a hash chain.
6. `/verify/{run_id}` proves the chain is intact and detects tampering.

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
  -d '{"action":"retrieve_internal","resource":{"resource_id":"vendornova_profile","classification":"public","source_type":"synthetic","allowed_groups":["procurement"]}}'
```

Run the local service stack:

```bash
bash scripts/run_local.sh
```

## Important files for Codex

- `AGENTS.md` — repo-level instructions Codex must read before work.
- `PROJECT_SOURCE_OF_TRUTH.md` — locked scope and product invariants.
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
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

## Public-claim discipline

Use: policy-mediated, permission-preserving for this synthetic corpus, approval-gated, tamper-evident, challenge prototype.

Do not claim: unhackable, guaranteed compliance, universal data-leak prevention, legal non-repudiation, Marketplace-approved, certified, or production-ready.
