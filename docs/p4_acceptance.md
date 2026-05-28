# P4 Acceptance - Judge Hardening

P4 is accepted when the public judging path is clearer, harder to
misunderstand, and easier to verify without expanding product scope or changing
the P0/P1/P2/P3 trust semantics.

## Acceptance Checks

- Public URL loads at `https://akretic-demo-ui-oes3slkexq-uc.a.run.app/`.
- The 90-second judge walkthrough in `README.md` remains accurate.
- UI or docs clearly show the trust boundary:
  - Gemini summarizes only permitted context.
  - Gate0-lite decides policy.
  - RAG DMZ-lite blocks denied text before model context.
  - `approval_required` gates sensitive side effects.
  - Evidence ledger verifies the run.
  - A2A shows agent collaboration through Agent Card / skill-call path.
- UI or docs clearly explain what Gemini does and does not decide.
- UI or docs clearly explain why denied source IDs may appear while denied text does not.
- Approval gate remains obvious in the public judge path.
- Evidence verification remains obvious in the public judge path.
- A2A proof remains visible with agent, skill, and `correlation_id`.
- Public claims remain bounded and do not imply launch approval, legal/compliance status, Marketplace status, or universal safety.
- `scripts/verify_judge_readiness.ps1` passes.
- `pytest -q` passes.
- `scripts/deploy_cloudrun.ps1 -PreflightOnly` passes.
- `scripts/verify_cloudrun_config.ps1` passes.
- `scripts/verify_cloudrun_p0.ps1 -RequirePublic` passes.
- No redeploy is required unless visible UI, runtime config, container contents, IAM, env vars, or deployed behavior changes.

## Scope Boundary

P4 does not change workflows, routes, resource classes, IAM, public URL shape,
private-service exposure, ADK posture, Agent Runtime, Registry, Firestore,
embeddings, search grounding, data sources, secrets, or P0/P1/P2/P3 trust
semantics.

Recommended branch: `p4/judge-hardening`.
