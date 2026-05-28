# P0 Deployment Notes

Date: 2026-05-28

## P4 Judge Hardening Update

Date: 2026-05-28

### Scope

- Added a public judge-readiness checklist focused on the 90-second proof path and trust boundary.
- Added a public judge-readiness verifier for the current Cloud Run URL.
- Linked P4 acceptance and judge-readiness docs from the README.
- No visible UI, runtime config, container image, IAM, env var, deployed verifier behavior, or service exposure changes were made.
- No redeploy was performed for P4, and screenshots were deferred to P5 because this pass did not change visible UI.

### Commands Run

```powershell
.\scripts\verify_judge_readiness.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
.\scripts\verify_cloudrun_config.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

### Verification Snapshot

- Judge-readiness verifier:
  - Public URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app/`
  - Public home, VendorNova review, approval decision, and sample evidence report all returned HTTP 200.
  - Run ID: `run_391260ba56cb4e41a237bafcd9ebfa3d`
  - Approval ID: `apr_26906e8b14594e7b81f5330e7822c910`
  - Vertex mode, denied-source proof, approval gate, A2A proof, evidence verification, and sample report validity were visible.
- Local test matrix: `29 passed`.
- Deploy preflight:
  - Account: `sean.w@akretic.com`
  - Project: `akretic-a2a-trust-gateway`
  - Region: `us-central1`
  - Billing: enabled
- Cloud Run config verifier:
  - `akretic-demo-ui`: public HTTP 200, revision `akretic-demo-ui-00012-ht7`
  - `akretic-root-orchestrator`: private unauthenticated HTTP 404, revision `akretic-root-orchestrator-00010-c5s`
  - `akretic-policy-agent`: private unauthenticated HTTP 404, revision `akretic-policy-agent-00010-xxq`
  - `akretic-knowledge-agent`: private unauthenticated HTTP 404, revision `akretic-knowledge-agent-00010-lpv`
  - `akretic-research-agent`: private unauthenticated HTTP 404, revision `akretic-research-agent-00010-55l`
  - `akretic-approval-evidence`: private unauthenticated HTTP 404, revision `akretic-approval-evidence-00010-85n`
- Proof-path verifier:
  - Run ID: `run_962bbb8f986d4d369aa2f56fdf5a83f0`
  - Approval ID: `apr_45f4b87fbb2c4dab80ee45dc3e0591f2`
  - `report_path`: `null`
  - `report_kept`: `false`
  - Model mode: `vertex`
  - Model: `gemini-2.5-flash`
  - Evidence report valid: `true`

## P3 Cloud Run Deployment Hardening Update

Date: 2026-05-28

### Scope

- Added deploy preflight-only mode; no resource changes are made by `-PreflightOnly`.
- Added read-only Cloud Run config verifier.
- Changed the proof-path verifier to delete transient evidence reports by default and retain them only with `-KeepReport`.
- Added rollback drill documentation with current revisions and previous ready rollback targets.
- No redeploy was performed for P3 because changes are docs and local script hardening only.
- No new resource classes, broad IAM grants, public private-service exposure, or trust-semantics changes were introduced.

### Commands Run

```powershell
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
.\scripts\verify_cloudrun_config.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic -KeepReport
```

### Verification Snapshot

- Deploy preflight:
  - Account: `sean.w@akretic.com`
  - Project: `akretic-a2a-trust-gateway`
  - Region: `us-central1`
  - Billing: enabled
  - Allowed services: `akretic-demo-ui`, `akretic-root-orchestrator`, `akretic-policy-agent`, `akretic-knowledge-agent`, `akretic-research-agent`, `akretic-approval-evidence`
- Cloud Run config verifier:
  - `akretic-demo-ui`: public HTTP 200, revision `akretic-demo-ui-00012-ht7`
  - `akretic-root-orchestrator`: private unauthenticated HTTP 404, revision `akretic-root-orchestrator-00010-c5s`
  - `akretic-policy-agent`: private unauthenticated HTTP 404, revision `akretic-policy-agent-00010-xxq`
  - `akretic-knowledge-agent`: private unauthenticated HTTP 404, revision `akretic-knowledge-agent-00010-lpv`
  - `akretic-research-agent`: private unauthenticated HTTP 404, revision `akretic-research-agent-00010-55l`
  - `akretic-approval-evidence`: private unauthenticated HTTP 404, revision `akretic-approval-evidence-00010-85n`
- Rollback targets documented in `docs/cloudrun_runbook.md`; no rollback traffic shift was executed.
- Proof-path verifier default cleanup run:
  - Run ID: `run_8d1fa6226c2c48e98e7ffc289a8b3e9c`
  - Approval ID: `apr_c4d58339a1eb4a99bb267a883b5eeaa9`
  - `report_path`: `null`
  - `report_kept`: `false`
  - Evidence report valid: `true`
- Proof-path verifier `-KeepReport` run:
  - Run ID: `run_e23a7e38fd074e9ca2a9b53fd38977fb`
  - Approval ID: `apr_7814ca3e9ff146d5a18c677bd873aa12`
  - `report_kept`: `true`
  - Retained report was deleted after verification because this was a script behavior check, not a submission artifact refresh.

## P2 Gemini/Vertex Hardening Deployment Update

Date: 2026-05-28

### Target Confirmed

- Account: `sean.w@akretic.com`
- Project: `akretic-a2a-trust-gateway`
- Billing: enabled
- Region: `us-central1`
- Model mode: `AKRETIC_GEMINI_MODE=vertex`
- Vertex project: `GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway`
- Vertex location: `GOOGLE_CLOUD_LOCATION=us-central1`
- Vertex model: `VERTEX_MODEL=gemini-2.5-flash`

### Resources Updated

No new resource classes were added. The P2 deploy updated the existing shared
container image and existing `akretic-*` Cloud Run services. IAM updates were
the existing deploy-script bindings for Cloud Build, Artifact Registry, Vertex
AI user on the runtime service account, evidence bucket object admin, and Cloud
Run invoker on private demo services.

- Final accepted build: `0f2cd287-6b29-47bb-8eff-f0bd1dbcd5cc`
- Final image digest: `sha256:cf185d4c75cd39cb38e4a9e2d6e0fd44f05f453d915a5f5d9e38a6d50868bfc2`
- Cloud Run revisions:
  - `akretic-demo-ui` revision `akretic-demo-ui-00012-ht7`: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
  - `akretic-root-orchestrator` revision `akretic-root-orchestrator-00010-c5s`: `https://akretic-root-orchestrator-oes3slkexq-uc.a.run.app`
  - `akretic-policy-agent` revision `akretic-policy-agent-00010-xxq`: `https://akretic-policy-agent-oes3slkexq-uc.a.run.app`
  - `akretic-knowledge-agent` revision `akretic-knowledge-agent-00010-lpv`: `https://akretic-knowledge-agent-oes3slkexq-uc.a.run.app`
  - `akretic-research-agent` revision `akretic-research-agent-00010-55l`: `https://akretic-research-agent-oes3slkexq-uc.a.run.app`
  - `akretic-approval-evidence` revision `akretic-approval-evidence-00010-85n`: `https://akretic-approval-evidence-oes3slkexq-uc.a.run.app`

### Commands Run

```powershell
gcloud config get-value account
gcloud config get-value project
gcloud billing projects describe akretic-a2a-trust-gateway --format=json
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
gcloud run services describe akretic-root-orchestrator --project akretic-a2a-trust-gateway --region us-central1 --format=json
gcloud run services list --project akretic-a2a-trust-gateway --region us-central1 --filter="metadata.name~akretic-" --format="table(metadata.name,status.latestReadyRevisionName,status.url)"
```

`scripts/deploy_cloudrun.ps1` was run during P2 hardening and again after the
public sample evidence report was moved into the demo UI build context. The
final accepted deployment is the build and revision set listed above.

### Verification

- Local test matrix: `29 passed`.
- Public Cloud Run verifier: `scripts/verify_cloudrun_p0.ps1 -RequirePublic` passed.
- Verifier run:
  - Run ID: `run_889bac8a968e4141b9fbf430ceadc74f`
  - Approval ID: `apr_9df1e374ae9941368a4bdb17b967194f`
  - Public unauthenticated GET `/`: HTTP 200.
  - Public unauthenticated UI `/run`: HTTP 200.
  - Public unauthenticated UI `/approval/decide`: HTTP 200.
  - Private evidence report endpoint: HTTP 200 with identity token.
  - Evidence report valid: `true`.
  - UI model proof: `Mode: vertex`, `Model: gemini-2.5-flash`, project `akretic-a2a-trust-gateway`, location `us-central1`.
  - Evidence model proof: `mode=vertex`, `model=gemini-2.5-flash`, `service_path=Vertex AI Gemini via google-genai`.
- Root Cloud Run env verification:
  - `AKRETIC_GEMINI_MODE=vertex`
  - `GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway`
  - `GOOGLE_CLOUD_LOCATION=us-central1`
  - `VERTEX_MODEL=gemini-2.5-flash`
- Public sample evidence report endpoint:
  - `/sample-evidence-report`: HTTP 200.
  - Sample run ID: `run_7768be07c8d74ec5a3a709344c3f4a54`.
  - Sample evidence report valid: `true`.
  - Sample model mode: `vertex`.

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
