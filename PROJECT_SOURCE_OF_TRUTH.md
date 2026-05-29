# Project Source of Truth

## Locked decision

| Area | Decision |
|---|---|
| Product name | Akretic A2A Trust Gateway |
| Submission frame | Track 3 challenge prototype for Google Cloud / Gemini Enterprise agent ecosystem |
| Buyer/use case | B2B procurement and security vendor-risk review |
| Core promise | Enterprise agents collaborate over A2A without letting the model decide what it may read, call, send, or approve |
| Build mode | Solo builder with AI coding agents; P0 proof chain over platform breadth |
| Runtime | Cloud Run first |
| Model path | Gemini through Vertex AI / Google Cloud approved path |
| Orchestration proof | Google ADK Workflow wrapper delegates to the verified root orchestrator |
| Data posture | Synthetic corpus only; no customer data; no private third-party data |
| Public posture | Challenge prototype; not a production certification, security guarantee, or Marketplace listing |

## P0 control invariants

1. Identity is derived from session/token/demo adapter, not the request body.
2. Gate0-lite produces deterministic `allow`, `deny`, or `approval_required` outcomes.
3. RAG DMZ-lite excludes restricted chunks before Gemini receives context.
4. A2A is functional, not decorative: Policy, Knowledge, and Approval/Evidence Agents expose Agent Cards and are called in the main workflow.
5. Sensitive side effects pause on `approval_required` until a reviewer decision is recorded.
6. Evidence ledger records material decisions and results in a tamper-evident hash chain.
7. Evidence verify/report endpoints require a role check in the demo.
8. Public copy stays inside tested claims.

## What we are building

A production-shaped prototype that governs one vendor-risk review workflow:

1. User starts VendorNova review.
2. Root orchestrator creates `run_id`.
3. Policy Agent authorizes retrieval and action intents.
4. Knowledge Agent returns only permitted synthetic internal context.
5. Research Agent returns seeded public-risk snippets.
6. Restricted executive memo request is denied before model context.
7. Exception draft/export request returns `approval_required`.
8. Reviewer approves or rejects.
9. Evidence Agent generates and verifies hash-chain report.

## What we are not building before P0

- GKE.
- Full SSO.
- Real enterprise connectors.
- Broad code execution.
- Marketplace packaging.
- Multiple verticals.
- Full policy administration console.
- Production certification claims.
- Universal data-leak prevention claims.

## Required demo personas

| Persona | Allowed | Denied / gated |
|---|---|---|
| `procurement_user` | Vendor intake docs, procurement policy, public vendor snippets | Executive/legal-only docs; external export requires approval |
| `security_reviewer` | Security policy, vendor questionnaire, risk evidence, public research | Executive-only strategy memo; export/destructive actions require approval |
| `legal_reviewer` | Contract checklist and legal review docs | Security-admin-only docs unless separately permitted |
| `admin` | Verify evidence, configure demo policies, inspect run logs | Cannot bypass evidence recording |

## Demo win condition

The judges must see three things in under two minutes:

1. agents coordinate over A2A;
2. restricted data is blocked before Gemini sees it;
3. approval and evidence controls are enforceable outside the model.
