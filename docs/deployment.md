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
- Synthetic corpus bucket: `gs://akretic-a2a-trust-gateway-corpus/p0-corpus/`
- Evidence bucket: `gs://akretic-a2a-trust-gateway-evidence/p0-evidence/`

## Deploy

Run from the repository root:

```powershell
.\scripts\deploy_cloudrun.ps1
```

Run the read-only preflight before any deploy-capable path:

```powershell
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
```

Verify after deployment:

```powershell
.\scripts\verify_cloudrun_p0.ps1
```

Require the public URL gate:

```powershell
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

Verify deployed Cloud Run configuration without changing resources:

```powershell
.\scripts\verify_cloudrun_config.ps1
```

The proof-path verifier deletes transient evidence reports by default. Keep a
report only when needed for debugging, audit capture, or submission packaging:

```powershell
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic -KeepReport
```

The script:

1. sets the active project to `akretic-a2a-trust-gateway`;
2. enables required P0 APIs;
3. creates the runtime service account if missing;
4. creates the Artifact Registry repository if missing;
5. creates private Cloud Storage evidence and synthetic corpus buckets if missing;
6. grants only the build/runtime permissions required for P0:
   - `roles/storage.objectViewer` for the Cloud Build execution service account on the Cloud Build source bucket;
   - `roles/artifactregistry.writer` for the Cloud Build execution service account on the `akretic` Artifact Registry repository;
   - `roles/logging.logWriter` for the Cloud Build execution service account on the project;
   - `roles/aiplatform.user` on the project;
   - `roles/storage.objectAdmin` on the evidence bucket;
   - `roles/storage.objectViewer` on the synthetic corpus bucket;
   - `roles/run.invoker` on private P0 Cloud Run services;
7. uploads the synthetic corpus metadata and Markdown documents to Cloud Storage;
8. builds one shared container image;
9. deploys private agent/root services behind Cloud Run IAM;
10. deploys only the demo UI as public by disabling the Cloud Run Invoker IAM check.

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
AKRETIC_RUNTIME_MODE=cloud
AKRETIC_CLOUD_RUN_AUTH=identity_token
GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
AKRETIC_CORPUS_BACKEND=gcs
AKRETIC_CORPUS_BUCKET=akretic-a2a-trust-gateway-corpus
AKRETIC_CORPUS_PREFIX=p0-corpus
AKRETIC_EVIDENCE_BUCKET=akretic-a2a-trust-gateway-evidence
AKRETIC_EVIDENCE_PREFIX=p0-evidence
AKRETIC_RAG_MODE=lexical
```

`EVIDENCE_GCS_BUCKET` and `EVIDENCE_GCS_PREFIX` remain compatibility aliases,
but new deployments should use the `AKRETIC_EVIDENCE_*` names. The corpus bucket
must contain `metadata.json` plus the referenced Markdown documents. Do not put
customer data, private third-party data, secrets, tokens, or production records
in the corpus bucket.

No customer data or real secrets are required for P0.

## Vertex/Gemini Verification

P2 requires the public demo path to run in cloud runtime mode with Vertex/Gemini:

- `AKRETIC_RUNTIME_MODE=cloud`
- `GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway`
- `GOOGLE_CLOUD_LOCATION=us-central1`
- `VERTEX_MODEL=gemini-2.5-flash`

The UI must show the model mode, model name, project, location, and prompt hash
for each review run. The evidence report summary must record the same model
path plus runtime mode, prompt hash, output/completion hash, permitted source
IDs, denied source IDs, and Research Agent seeded source IDs/citations. Denied
source IDs are allowed as proof; denied source text and the
`AKRETIC_EXEC_ONLY_CANARY_DO_NOT_SUMMARIZE` canary are not allowed in the
prompt, UI, output, or evidence report.

Expected failure classes are credential/auth, service-account permission, quota,
model/project/location configuration, disabled API, billing/org policy, and bad
local configuration. Do not switch to AI Studio or broaden IAM to resolve these;
stop and record the exact blocker.

## Redeploy Boundary

Do not redeploy for docs-only or local verifier-only changes. Redeploy only when
runtime config, container image contents, Cloud Run service settings, IAM,
environment variables, deployed verifier behavior, or public UI behavior changes.

Rollback and incident commands are documented in `docs/cloudrun_runbook.md`.

## Final Handoff Packet

Create the final cloud review packet only from public Cloud Run URLs:

```powershell
.\.venv\Scripts\python.exe scripts\make_final_handoff.py --mode cloud --base-url https://<PUBLIC_DEMO_URL> --root-url https://<ROOT_SERVICE_URL> --policy-url https://<POLICY_SERVICE_URL> --knowledge-url https://<KNOWLEDGE_SERVICE_URL> --research-url https://<RESEARCH_SERVICE_URL> --approval-url https://<APPROVAL_EVIDENCE_SERVICE_URL> --project-label <PROJECT_OR_REDACTED_PROJECT_LABEL> --demo-ui-revision <DEMO_UI_REVISION> --root-revision <ROOT_REVISION> --policy-revision <POLICY_REVISION> --knowledge-revision <KNOWLEDGE_REVISION> --research-revision <RESEARCH_REVISION> --approval-revision <APPROVAL_REVISION>
```

The script runs `scripts/p0_verify.py --expect-vertex --fail-on-local
--expect-corpus-backend gcs --expect-freeform-playground
--expect-corpus-explorer --expect-decision-receipts`, captures raw responses
and screenshots, writes `FINAL_REVIEW.md`, and refuses a cloud packet that
contains localhost/local deterministic proof strings or missing cloud
model/project/location/revision/corpus-backend metadata.
