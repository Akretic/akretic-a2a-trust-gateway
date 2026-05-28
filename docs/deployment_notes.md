# P0 Deployment Notes

Date: 2026-05-28

## Target

- Account: `sean.w@akretic.com`
- Project: `akretic-a2a-trust-gateway`
- Project number: `472908523998`
- Region: `us-central1`
- Image: `us-central1-docker.pkg.dev/akretic-a2a-trust-gateway/akretic/akretic-p0:p0-latest`
- Latest build: `ff289fcd-1606-4b49-b0d7-b8efcf45031c`
- Latest image digest: `sha256:e0f28e860e0c3e38d340282bca32e13f4fa81e93640e49df9b575233f323325a`

## Resources Created Or Updated

- Runtime service account: `akretic-p0-runtime@akretic-a2a-trust-gateway.iam.gserviceaccount.com`
- Artifact Registry repository: `akretic`
- Evidence bucket: `gs://akretic-a2a-trust-gateway-evidence/p0-evidence/`
- Cloud Build source bucket: `gs://akretic-a2a-trust-gateway_cloudbuild/`
- Cloud Build execution service account: `472908523998-compute@developer.gserviceaccount.com`
- Cloud Run services:
  - `akretic-demo-ui` revision `akretic-demo-ui-00004-8gc`: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
  - `akretic-root-orchestrator` revision `akretic-root-orchestrator-00004-4p5`: `https://akretic-root-orchestrator-oes3slkexq-uc.a.run.app`
  - `akretic-policy-agent` revision `akretic-policy-agent-00004-rwp`: `https://akretic-policy-agent-oes3slkexq-uc.a.run.app`
  - `akretic-knowledge-agent` revision `akretic-knowledge-agent-00004-dmm`: `https://akretic-knowledge-agent-oes3slkexq-uc.a.run.app`
  - `akretic-research-agent` revision `akretic-research-agent-00004-4wf`: `https://akretic-research-agent-oes3slkexq-uc.a.run.app`
  - `akretic-approval-evidence` revision `akretic-approval-evidence-00004-nln`: `https://akretic-approval-evidence-oes3slkexq-uc.a.run.app`

## IAM Changes

- `akretic-p0-runtime@...`
  - `roles/aiplatform.user` on the project.
  - `roles/storage.objectAdmin` on `gs://akretic-a2a-trust-gateway-evidence`.
  - `roles/run.invoker` on private P0 Cloud Run services.
- `472908523998-compute@developer.gserviceaccount.com`
  - `roles/storage.objectViewer` on `gs://akretic-a2a-trust-gateway_cloudbuild`.
  - `roles/artifactregistry.writer` on the `akretic` Artifact Registry repository.
  - `roles/logging.logWriter` on the project.

No owner/editor grants were added by the deploy work.

## Commands Run

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1
gcloud run services add-iam-policy-binding akretic-demo-ui --project akretic-a2a-trust-gateway --region us-central1 --member allUsers --role roles/run.invoker
gcloud auth print-identity-token
.\scripts\verify_cloudrun_p0.ps1
```

The deploy script also ran the documented `gcloud services enable`, Artifact Registry,
Cloud Storage, Cloud Build, and Cloud Run deploy/update commands for the P0 resources.

## Verification

- Local test matrix: `17 passed`.
- Cloud Build latest build: `SUCCESS`.
- Authenticated Cloud Run smoke:
  - Run ID: `run_9e24c7f1d4d0452989c0e39c0e48a4c1`
  - Approval ID: `apr_cde153b3c70c4d5d842c7110a3b239c7`
  - Public unauthenticated GET `/`: HTTP 403 until org policy is fixed.
  - UI `/run`: HTTP 200.
  - UI `/approval/decide`: HTTP 200.
  - Evidence report endpoint: HTTP 200.
- Sample evidence report: `artifacts/sample-evidence-report-run_9e24c7f1d4d0452989c0e39c0e48a4c1.json`
- Sample screenshots:
  - `output/playwright/demo-home.png`
  - `output/playwright/demo-review-result.png`
- Evidence report facts:
  - `verification.valid`: `true`
  - `event_count`: `19`
  - `a2a_call_count`: `4`
  - Vertex model path: `Vertex AI Gemini via google-genai`
  - Permitted source IDs: `vendornova_profile`, `procurement_policy`
  - Denied source IDs: `vendornova_security_questionnaire`, `infosec_vendor_policy`, `contract_review_checklist`, `executive_acquisition_memo`
  - Reviewer decision: `approved` by `user-security-001`

## Current Blocker

The demo UI is deployed but is not public yet. The required public invoker binding fails:

```text
FAILED_PRECONDITION: One or more users named in the policy do not belong to a permitted customer, perhaps due to an organization policy.
```

Current `akretic-demo-ui` IAM policy has no `allUsers` binding. The private root service
has only the runtime service account as `roles/run.invoker`.

Manual options:

1. Add a domain-restricted-sharing exception for this project/service so
   `allUsers` can be granted `roles/run.invoker` on `akretic-demo-ui`.
2. Move the demo project under a folder/org policy that allows public Cloud Run
   invoker bindings for demo workloads.
3. Use a separate public-allowed GCP project and update `.env.example`,
   `docs/deployment.md`, and this service map.

The project also emits a non-blocking warning that it lacks an `environment` tag.
Use `Development` or `Test` if the organization requires project environment tags.
