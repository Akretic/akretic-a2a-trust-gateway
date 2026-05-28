# P0 Deployment Notes

Date: 2026-05-28

## Target

- Account: `sean.w@akretic.com`
- Project: `akretic-a2a-trust-gateway`
- Project number: `472908523998`
- Region: `us-central1`
- Image: `us-central1-docker.pkg.dev/akretic-a2a-trust-gateway/akretic/akretic-p0:p0-latest`
- Latest build: `20aadc2f-ed83-4417-a9c1-e4f3a68162eb`
- Latest image digest: `sha256:9e71b299158b0814b3a7b8fab3fad76df14394399f5f8a439159b7365d5ae80d`

## Resources Created Or Updated

- Runtime service account: `akretic-p0-runtime@akretic-a2a-trust-gateway.iam.gserviceaccount.com`
- Artifact Registry repository: `akretic`
- Evidence bucket: `gs://akretic-a2a-trust-gateway-evidence/p0-evidence/`
- Cloud Build source bucket: `gs://akretic-a2a-trust-gateway_cloudbuild/`
- Cloud Build execution service account: `472908523998-compute@developer.gserviceaccount.com`
- Cloud Run services:
  - `akretic-demo-ui` revision `akretic-demo-ui-00005-qc5`: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
  - `akretic-root-orchestrator` revision `akretic-root-orchestrator-00005-dp7`: `https://akretic-root-orchestrator-oes3slkexq-uc.a.run.app`
  - `akretic-policy-agent` revision `akretic-policy-agent-00005-98p`: `https://akretic-policy-agent-oes3slkexq-uc.a.run.app`
  - `akretic-knowledge-agent` revision `akretic-knowledge-agent-00005-ddb`: `https://akretic-knowledge-agent-oes3slkexq-uc.a.run.app`
  - `akretic-research-agent` revision `akretic-research-agent-00005-khj`: `https://akretic-research-agent-oes3slkexq-uc.a.run.app`
  - `akretic-approval-evidence` revision `akretic-approval-evidence-00005-r24`: `https://akretic-approval-evidence-oes3slkexq-uc.a.run.app`

## IAM Changes

- `akretic-demo-ui`
  - Public access uses Cloud Run `run.googleapis.com/invoker-iam-disabled=true`.
  - No `allUsers` IAM binding is required.
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
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

The deploy script also ran the documented `gcloud services enable`, Artifact Registry,
Cloud Storage, Cloud Build, and Cloud Run deploy/update commands for the P0 resources.

## Verification

- Local test matrix: `17 passed`.
- Cloud Build latest build: `SUCCESS`.
- Public Cloud Run smoke:
  - Run ID: `run_be30e4f10ef7483d9f6695fd64d5dfa3`
  - Approval ID: `apr_91f08a47a6f646bcb3409a7d9014438e`
  - Public unauthenticated GET `/`: HTTP 200.
  - Public unauthenticated UI `/run`: HTTP 200.
  - Public unauthenticated UI `/approval/decide`: HTTP 200.
  - Evidence report endpoint: HTTP 200.
- Sample evidence report: `artifacts/sample-evidence-report-run_be30e4f10ef7483d9f6695fd64d5dfa3.json`
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

## Public Access Resolution

The Akretic organization policy blocks `allUsers` IAM bindings. The demo UI is
public through the Cloud Run no-invoker IAM check mode instead. Private agent,
root, and approval/evidence services keep the invoker IAM check enabled and only
grant `roles/run.invoker` to the runtime service account.

The project also emits a non-blocking warning that it lacks an `environment` tag.
Existing org tag keys and project tag bindings were checked on 2026-05-28 and
none existed. Creating the minimal org tag key `environment` for value
`development` was attempted with `sean.w@akretic.com`, but Google Cloud denied
`resourcemanager.tagKeys.create` on `organizations/287336668994`. A human with
Tag Admin rights should create or bind `environment=development` if the Akretic
organization requires project environment tags.
