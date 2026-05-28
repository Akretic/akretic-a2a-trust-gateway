# Deployment

## Target

- Project ID: `akretic-a2a-trust-gateway`
- Region: `us-central1`
- Public service: `akretic-demo-ui`
- Private Cloud Run services:
  - `akretic-root-orchestrator`
  - `akretic-policy-agent`
  - `akretic-knowledge-agent`
  - `akretic-research-agent`
  - `akretic-approval-evidence`
- Artifact Registry repository: `akretic`
- Runtime service account: `akretic-p0-runtime@akretic-a2a-trust-gateway.iam.gserviceaccount.com`
- Evidence bucket: `gs://akretic-a2a-trust-gateway-evidence/p0-evidence/`

## Deploy

Run from the repository root:

```powershell
.\scripts\deploy_cloudrun.ps1
```

The script:

1. sets the active project to `akretic-a2a-trust-gateway`;
2. enables required P0 APIs;
3. creates the runtime service account if missing;
4. creates the Artifact Registry repository if missing;
5. creates a private Cloud Storage evidence bucket if missing;
6. grants only the runtime permissions required for P0:
   - `roles/aiplatform.user` on the project;
   - `roles/storage.objectAdmin` on the evidence bucket;
   - `roles/run.invoker` on private P0 Cloud Run services;
7. builds one shared container image;
8. deploys private agent/root services behind Cloud Run IAM;
9. deploys only the demo UI as public.

## Runtime Boundaries

The demo UI is public for judging. Agent, root, and approval/evidence services are private
Cloud Run services. The public UI calls private services with the runtime service account.

Evidence and verify/report APIs are not exposed directly to unauthenticated public traffic.
They still enforce demo persona role checks in application code, but Cloud Run IAM is the
first boundary in the deployed P0 path.

## Required Environment

The deployed root/UI services use:

```text
AKRETIC_GEMINI_MODE=vertex
AKRETIC_CLOUD_RUN_AUTH=identity_token
GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
EVIDENCE_GCS_BUCKET=akretic-a2a-trust-gateway-evidence
EVIDENCE_GCS_PREFIX=p0-evidence
```

No customer data or real secrets are required for P0.
