# P3 Acceptance - Cloud Run Deployment Hardening

P3 is accepted when the existing Cloud Run deployment is safer to repeat,
verify, troubleshoot, and roll back without changing the P0/P1/P2 trust
semantics.

## Acceptance Checks

- `scripts/deploy_cloudrun.ps1 -PreflightOnly` passes before any deploy-capable command path.
- Deploy preflight fails before resource changes if the active account, active project, billing status, target project, target region, or service allowlist is wrong.
- `scripts/verify_cloudrun_config.ps1` passes against the deployed Cloud Run services.
- Cloud Run config verifier confirms:
  - all expected `akretic-*` services exist;
  - services are ready and serving latest ready revisions at 100% traffic;
  - runtime service account is `akretic-p0-runtime@akretic-a2a-trust-gateway.iam.gserviceaccount.com`;
  - required Vertex/Gemini and evidence environment variables match P2 values;
  - demo UI is public;
  - root, agent, and approval/evidence services do not disable the Cloud Run invoker IAM check;
  - private services do not return unauthenticated HTTP 200;
  - no `allUsers` or `allAuthenticatedUsers` IAM member is present on the Cloud Run service IAM policies.
- `scripts/verify_cloudrun_p0.ps1 -RequirePublic` deletes transient verifier evidence reports by default.
- `scripts/verify_cloudrun_p0.ps1 -RequirePublic -KeepReport` can retain a report for debugging, audit capture, or submission packaging.
- A lightweight rollback drill is documented with current revisions, rollback targets, and exact commands.
- No rollback traffic shift is executed unless explicitly approved.
- Deployment docs state when redeploy is required and when docs/script-only work does not require redeploy.
- `pytest -q` passes.
- `scripts/verify_cloudrun_p0.ps1 -RequirePublic` passes.

## Scope Boundary

P3 does not add new resource classes, broaden IAM, expose private services
publicly, change the public demo URL shape, or alter P0/P1/P2 identity, policy,
RAG filtering, approval, evidence, A2A, or Gemini trust semantics.

Recommended branch: `p3/cloudrun-hardening`.
