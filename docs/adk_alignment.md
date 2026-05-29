# ADK Alignment Hardening

P6 started as ADK alignment documentation. Final challenge-readiness remediation
adds a `google-adk` Workflow wrapper to the root entrypoint while preserving the
verified Cloud Run proof path and trust semantics.

Preferred public wording:

```text
The current proof path runs on Cloud Run with Vertex/Gemini summarization and A2A Agent Card skill-call wiring. The root entrypoint uses a Google ADK Workflow wrapper that delegates to the verified orchestrator path. Authorization, retrieval filtering, approvals, and evidence remain outside Gemini and are not delegated to the model.
```

Short wording:

```text
The root orchestration layer is ADK-wrapped, while the verified demo path remains Cloud Run + Vertex/Gemini + A2A Agent Card skill calls.
```

## What Changed

- `agents/root_orchestrator/adk_alignment.py` adds an `AdkRootInvocation`
  envelope, a `google-adk` `Workflow`, and `run_adk_aligned_vendor_review`.
- The wrapper delegates to
  `agents.root_orchestrator.main.run_vendor_review_workflow`.
- The public `/run_vendor_review` endpoint enters the wrapper, which delegates
  immediately to the existing orchestrator.
- The wrapper does not change Cloud Run service shape, broaden IAM, add Agent
  Runtime, add Agent Registry, or replace the root orchestrator.
- `tests/test_adk_alignment.py` proves the wrapper keeps the existing controls
  in the path.

## ADK Concept Mapping

| ADK concept | Current verified component | Proof boundary |
|---|---|---|
| Root agent / workflow coordinator | Google ADK `Workflow` wrapper -> Root Orchestrator `run_vendor_review_workflow` | The wrapper is the root entrypoint delegate and does not create a second product workflow. |
| Tool call | A2A Agent Card / skill-call adapter in `common/a2a_client.py` | Agent Cards are resolved before skills are called and A2A events record Agent Card URL, caller, callee, skill/intent, `correlation_id`, event ID, and event hash. |
| Policy / guardrail before tool or model work | Gate0-lite Policy Agent | Gate0-lite remains the policy decision point. Gemini does not decide authorization. |
| Retrieval context assembly | RAG DMZ-lite Knowledge Agent | Restricted chunks are filtered before prompt assembly. Denied source IDs may appear as proof, but denied source text does not enter context. |
| Model call | Vertex/Gemini adapter in `common/gemini.py` | Gemini summarizes permitted synthetic context only and output guards block denied canary text and completed pending approvals. |
| Human approval | Approval/Evidence Agent | Sensitive external action returns `approval_required` and remains blocked pending reviewer decision. |
| Event trace / verification | Hash-chained evidence ledger | Material A2A, policy, retrieval, approval, model, and verification events are recorded and verified. |

## Wrapper Boundary

The P6 wrapper is an adapter, not a new product surface:

- It uses `google-adk==2.0.0` to build `akretic_root_vendor_review_workflow`.
- It accepts an agent-shaped invocation envelope.
- It passes persona, query, vendor, optional `run_id`, optional model mode, and
  optional body claims into the verified workflow.
- Request-body claims still cannot upgrade identity because the existing root
  path derives the actor from the trusted demo persona adapter/header.
- The result includes `adk_runtime` and `adk_alignment` metadata so tests, UI,
  and local diagnostics can show that the wrapper delegated to the verified
  orchestrator and did not replace trust behavior.

## Non-Claims

- This is not full ADK-native orchestration.
- This is not Agent Runtime or Agent Registry integration.
- This does not add Firestore, embeddings, Google Search grounding, new data
  sources, or new workflows.
- This does not add a new public route or alternate production path.
- This does not move authorization, retrieval filtering, approval, or evidence
  decisions into Gemini.

## Local Diagnostic

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_adk_alignment.py -q
```

The broader P6 merge bar remains the full verifier set in
`docs/p6_acceptance.md`.
