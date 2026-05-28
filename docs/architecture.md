# Architecture

```text
Demo UI
  -> ADK Root Orchestrator / root service
      -> Policy Agent / Gate0-lite
      -> Knowledge Agent / RAG DMZ-lite
      -> Research Agent / seeded public snippets
      -> Approval/Evidence Agent
          -> Evidence Ledger
          -> Verify Report
      -> Vertex AI Gemini for permitted-context summarization
```

## Invariant

Identity, retrieval, tool calls, egress, approvals, and evidence are controlled outside the model.

## Data flow

1. UI sends vendor-risk request with demo persona header.
2. Root derives actor identity from adapter/header/session.
3. Root creates `run_id`.
4. Root calls Policy Agent before material actions.
5. Knowledge Agent retrieves only chunks permitted by metadata and policy.
6. Root passes only permitted chunks to Gemini.
7. Sensitive side-effect requests create approval request.
8. Evidence ledger records all material decisions and results.

## Trust boundary

Gemini may plan and summarize. Gemini does not decide authorization, approval, identity, source access, or evidence validity.
