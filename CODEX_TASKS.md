# Codex Goal Mode Task Packet

Use `/plan` for ambiguous work, then `/goal` for execution. Keep every goal bounded and testable.

Before selecting work, read `PROJECT_SOURCE_OF_TRUTH.md`, then
`docs/priority_ladder.md`. P0, P1, P2, P3, and P4 are cleared; P5 Submission
package is the active lane. P6 Google stretch and P7 post-challenge
productization are non-blocking and must not displace P5 work.

## Current active lane

P5 Submission package is the active lane. The P0 tickets below are
regression and reference material only unless tests fail or the user explicitly
assigns P0 regression work. Do not rebuild cleared P0/P1 work just because the
historical ticket sequence is still documented here.

## Goal mode operating rule

A good goal includes:

- exact feature;
- files likely to change;
- definition of done;
- command that proves completion;
- pause condition.

## Master goal

```text
/goal Stabilize the Akretic P0 proof chain for the VendorNova demo. Preserve the repo architecture and source-of-truth constraints. Implement one bounded feature at a time with tests. The proof chain is complete only when identity spoofing is rejected, Gate0-lite returns allow/deny/approval_required, RAG DMZ-lite filters restricted chunks before context, Policy and Knowledge Agent Cards are served, root calls A2A endpoints in the main workflow, side effects pause for approval, evidence verification detects tampering, and public claims tests pass. Run pytest -q after each meaningful change and pause if scope conflicts with PROJECT_SOURCE_OF_TRUTH.md.
```

## Ticket sequence

### T01 — Repo sanity and test baseline

```text
/goal Verify the starter repository runs locally. Do not add features. Install dependencies, run pytest -q, inspect failing tests if any, and produce a concise fix plan. Definition of done: pytest -q passes or each failure is mapped to an exact next ticket.
```

### T02 — Gate0-lite policy evaluator

```text
/goal Implement or harden Gate0-lite policy evaluation. Inputs are actor, action, resource, and context. Output must be allow, deny, or approval_required with reason, correlation_id, and timestamp. Do not touch ADK/Gemini. Definition of done: tests/test_policy_decisions.py passes and README includes the local curl command.
```

### T03 — Identity spoofing protection

```text
/goal Harden demo identity derivation. User/tenant/groups/role must come from session/header/demo adapter only; request-body claims cannot upgrade privilege. Definition of done: tests/test_identity_spoofing.py passes and at least one negative API test exists.
```

### T04 — RAG DMZ-lite retrieval filter

```text
/goal Implement RAG DMZ-lite metadata filtering over the synthetic corpus. Restricted chunks must be excluded before any prompt/context assembly. Denied source_ids may be recorded, but denied content must not be summarized or returned. Definition of done: tests/test_rag_filtering.py passes and a sample denied executive memo retrieval writes evidence.
```

### T05 — Evidence ledger

```text
/goal Implement append-only hash-chained evidence events and verify endpoint behavior. Every event must include run_id, actor_id, agent_id, action, resource_id, outcome, reason, prev_hash, event_hash, and timestamp. Definition of done: tests/test_evidence_verify.py passes, including tamper detection.
```

### T06 — A2A Agent Cards

```text
/goal Expose valid Agent Cards for Policy Agent and Knowledge Agent at both /agent-card.json and /.well-known/agent-card.json. Include name, description, version, endpoint URL, skills, capabilities, and authentication notes. Definition of done: tests/test_a2a_cards.py passes and curl examples work locally.
```

### T07 — Root remote-call adapter

```text
/goal Build a thin HTTP A2A client adapter for the root orchestrator. It must resolve Agent Cards, call advertised skills, pass run_id/correlation_id, and record caller/callee/skill/result evidence. Do not bypass policy. Definition of done: tests/test_a2a_remote_call_logged.py passes.
```

### T08 — Approval gate

```text
/goal Implement approval_required path for draft/export side effects. Side effects must not complete until a reviewer decision is recorded. Definition of done: tests/test_approval_gate.py passes and UI or API can approve/reject.
```

### T09 — Gemini root integration

```text
/goal Integrate the root orchestrator with Gemini through the Google Cloud approved Vertex AI path. A thin HTTP Agent Card/A2A adapter is acceptable for P0 if direct ADK integration would block the proof path. Gemini may summarize only permitted context. It must not decide policy, reveal denied document contents, or claim approval-gated actions completed. Definition of done: local VendorNova review succeeds with permitted sources and denied memo stays out of model context.
```

### T10 — Cloud Run deployment

```text
/goal Deploy the P0 services to Cloud Run using the infra/cloudrun scaffold. Required services: demo-ui, root-orchestrator, policy-agent, knowledge-agent, research-agent, approval-evidence. Definition of done: public demo URL runs the full happy path, logs include run_id, and README has judging instructions.
```

### T11 — Submission hardening

```text
/goal Harden final submission materials. Remove unimplemented stretch claims, run the public copy claim test, update demo script, and document limitations. Definition of done: pytest -q passes, docs/submission_answers_public.md has no banned claims, and docs/demo_script.md matches the running app.
```
