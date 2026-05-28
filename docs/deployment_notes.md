# P0 Deployment Notes

Date: 2026-05-28

## P1 Demo-Path Polish Deployment Update

Date: 2026-05-28

### Final Acceptance Polish

Date: 2026-05-28

- Scope: public UI label-only polish for P1 acceptance; no runtime behavior changes.
- Build: `628803d2-1547-41be-a272-e51fd1b4719e`
- Image digest: `sha256:1819db7fb779b7420cdef0e67601afb7c0c7b835f87b0c0461c96f1a70d77cdf`
- Cloud Run service updated: `akretic-demo-ui` revision `akretic-demo-ui-00009-hmf`.
- Private agent service revisions were not redeployed for this final label polish.
- Commands run:

```powershell
gcloud config get-value account
gcloud config get-value project
gcloud billing projects describe akretic-a2a-trust-gateway --format=json
.\.venv\Scripts\python.exe -m pytest -q
gcloud builds submit . --project akretic-a2a-trust-gateway --config infra/cloudrun/cloudbuild.yaml --substitutions _IMAGE=us-central1-docker.pkg.dev/akretic-a2a-trust-gateway/akretic/akretic-p0:p0-latest
gcloud run deploy akretic-demo-ui --project akretic-a2a-trust-gateway --region us-central1 --image us-central1-docker.pkg.dev/akretic-a2a-trust-gateway/akretic/akretic-p0:p0-latest --service-account akretic-p0-runtime@akretic-a2a-trust-gateway.iam.gserviceaccount.com --no-invoker-iam-check --set-env-vars <demo-ui-env-vars>
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

- Verification:
  - `pytest -q`: `19 passed`.
  - `scripts/verify_cloudrun_p0.ps1 -RequirePublic`: passed.
  - Live UI check: no public `P1` label, Policy tile says `external action is approval_required`, evidence metric says `valid hash chain`.

### Target Confirmed

- Account: `sean.w@akretic.com`
- Project: `akretic-a2a-trust-gateway`
- Billing: enabled
- Region: `us-central1`

### Resources Updated

No new resource classes were added. The P1 deploy updated the existing demo
container image, existing `akretic-*` Cloud Run services, and existing least
privilege IAM bindings managed by `scripts/deploy_cloudrun.ps1`.

- Latest build: `b8a50161-2cd7-4ebb-9d26-2fcbc05486f7`
- Latest image digest: `sha256:14a616819ec56308739245279aaddca270e99e9a7b0e3123d20424eb77976301`
- Cloud Run revisions:
  - `akretic-demo-ui` revision `akretic-demo-ui-00007-2d4`: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
  - `akretic-root-orchestrator` revision `akretic-root-orchestrator-00007-9pf`: `https://akretic-root-orchestrator-oes3slkexq-uc.a.run.app`
  - `akretic-policy-agent` revision `akretic-policy-agent-00007-4rq`: `https://akretic-policy-agent-oes3slkexq-uc.a.run.app`
  - `akretic-knowledge-agent` revision `akretic-knowledge-agent-00007-rnx`: `https://akretic-knowledge-agent-oes3slkexq-uc.a.run.app`
  - `akretic-research-agent` revision `akretic-research-agent-00007-dw6`: `https://akretic-research-agent-oes3slkexq-uc.a.run.app`
  - `akretic-approval-evidence` revision `akretic-approval-evidence-00007-pv6`: `https://akretic-approval-evidence-oes3slkexq-uc.a.run.app`

### Commands Run

```powershell
gcloud config get-value account
gcloud config get-value project
gcloud billing projects describe akretic-a2a-trust-gateway --format=json
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

An ADC mint check was completed before deployment; the token value is not
recorded in repository docs.

`scripts/deploy_cloudrun.ps1` was run twice during P1: once for the full polish
deploy and once after a UI summary-rendering fix. The script re-ran its documented
API-enable, Artifact Registry, Cloud Storage, Cloud Build, Cloud Run, and
least-privilege IAM update steps for the demo resources.

### Verification

- Local test matrix: `19 passed`.
- Public Cloud Run smoke after final deploy:
  - Run ID: `run_d7dd27bd36314714860355539146ebbc`
  - Approval ID: `apr_ee42821c030b4c99afd8d0d5e8a6b7da`
  - Public unauthenticated GET `/`: HTTP 200.
  - Public unauthenticated UI `/run`: HTTP 200.
  - Public unauthenticated UI `/approval/decide`: HTTP 200.
  - Evidence report endpoint: HTTP 200.
  - Evidence report valid: `true`.
- Browser/public UI checks:
  - Judge walkthrough visible.
  - `Denied before model context: executive_acquisition_memo.` visible.
  - `approval_required` visible and separate from completed actions.
  - A2A proof shows agent, skill, and `correlation_id`.
  - Evidence verification shows valid hash chain and event count.
- Refreshed screenshots:
  - `output/playwright/demo-home.png`
  - `output/playwright/demo-review-result.png`
  - `output/playwright/screenshot-metadata.json`
- Refreshed no-video P1 bundle:
  - `dist/akretic-a2a-trust-gateway-p1-submission.zip`

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

The project environment warning is cleared. The Akretic organization now has
tag key `287336668994/environment`, tag value
`287336668994/environment/Development`, and a binding on project
`//cloudresourcemanager.googleapis.com/projects/472908523998`.
