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

Verify after deployment:

```powershell
.\scripts\verify_cloudrun_p0.ps1
```

Require the public URL gate:

```powershell
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

The script:

1. sets the active project to `akretic-a2a-trust-gateway`;
2. enables required P0 APIs;
3. creates the runtime service account if missing;
4. creates the Artifact Registry repository if missing;
5. creates a private Cloud Storage evidence bucket if missing;
6. grants only the build/runtime permissions required for P0:
   - `roles/storage.objectViewer` for the Cloud Build execution service account on the Cloud Build source bucket;
   - `roles/artifactregistry.writer` for the Cloud Build execution service account on the `akretic` Artifact Registry repository;
   - `roles/logging.logWriter` for the Cloud Build execution service account on the project;
   - `roles/aiplatform.user` on the project;
   - `roles/storage.objectAdmin` on the evidence bucket;
   - `roles/run.invoker` on private P0 Cloud Run services;
7. builds one shared container image;
8. deploys private agent/root services behind Cloud Run IAM;
9. deploys only the demo UI as public by disabling the Cloud Run Invoker IAM check.

## Runtime Boundaries

The demo UI is public for judging. It uses Cloud Run's no-invoker IAM check mode
instead of an `allUsers` IAM binding because the Akretic organization policy blocks
domain-unrestricted IAM principals. Agent, root, and approval/evidence services are
private Cloud Run services. The public UI calls private services with the runtime
service account.

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

## Vertex/Gemini Verification

P2 requires the public demo path to run in Vertex mode:

- `AKRETIC_GEMINI_MODE=vertex`
- `GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway`
- `GOOGLE_CLOUD_LOCATION=us-central1`
- `VERTEX_MODEL=gemini-2.5-flash`

The UI must show the model mode, model name, project, and location for each
review run. The evidence report summary must record the same model path plus a
prompt hash, permitted source IDs, and denied source IDs. Denied source IDs are
allowed as proof; denied source text is not allowed in the prompt, UI, output,
or evidence report.

Expected failure classes are credential/auth, service-account permission, quota,
model/project/location configuration, disabled API, billing/org policy, and bad
local configuration. Do not switch to AI Studio or broaden IAM to resolve these;
stop and record the exact blocker.
