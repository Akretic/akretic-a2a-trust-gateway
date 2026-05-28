# Cloud Run Runbook

This runbook is for the Akretic A2A Trust Gateway challenge prototype in
project `akretic-a2a-trust-gateway`, region `us-central1`.

## Safety Rules

- Do not create resources outside `akretic-a2a-trust-gateway`.
- Do not broaden IAM or add public IAM members.
- Do not expose root, agent, approval, evidence, or admin APIs publicly.
- Do not shift Cloud Run traffic or perform rollback unless explicitly approved.
- Do not store secrets, tokens, identity tokens, or customer data in the repo.

## Preflight

Run read-only preflight before any deploy-capable path:

```powershell
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
```

Expected target:

- Account: `sean.w@akretic.com`
- Project: `akretic-a2a-trust-gateway`
- Region: `us-central1`
- Billing: enabled
- Runtime service account: `akretic-p0-runtime@akretic-a2a-trust-gateway.iam.gserviceaccount.com`

## Config Verification

Run the read-only Cloud Run config verifier:

```powershell
.\scripts\verify_cloudrun_config.ps1
```

The verifier checks service readiness, service account, Vertex/Gemini env vars,
evidence env vars, public/private exposure, and Cloud Run IAM policy members.
The demo UI should return unauthenticated HTTP 200. Private services should not
return unauthenticated HTTP 200; current Cloud Run behavior returns HTTP 404 for
the private service unauthenticated checks.

Run the full proof-path verifier:

```powershell
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

By default the proof-path verifier does not keep transient evidence reports.
Use `-KeepReport` only for debugging, audit capture, or submission packaging:

```powershell
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic -KeepReport
```

## When To Redeploy

Do not redeploy for docs-only or local verifier-only changes.

Redeploy only when runtime config, container image contents, Cloud Run service
settings, IAM, environment variables, deployed verifier behavior, or public UI
behavior changes.

## Inspect Current State

```powershell
gcloud run services list --project akretic-a2a-trust-gateway --region us-central1 --filter="metadata.name~akretic-" --format="table(metadata.name,status.latestReadyRevisionName,status.url)"
gcloud run services describe akretic-root-orchestrator --project akretic-a2a-trust-gateway --region us-central1 --format=json
gcloud run services get-iam-policy akretic-root-orchestrator --project akretic-a2a-trust-gateway --region us-central1 --format=json
```

## Logs

Use run IDs from the verifier output when inspecting logs:

```powershell
gcloud run services logs read akretic-demo-ui --project akretic-a2a-trust-gateway --region us-central1 --limit=100
gcloud run services logs read akretic-root-orchestrator --project akretic-a2a-trust-gateway --region us-central1 --limit=100
gcloud run services logs read akretic-approval-evidence --project akretic-a2a-trust-gateway --region us-central1 --limit=100
```

## Rollback Drill

This is a documented drill only. Do not run rollback commands unless explicitly
approved.

Current accepted revisions from the P2 deployment:

| Service | Current revision | Rollback target |
|---|---|---|
| `akretic-demo-ui` | `akretic-demo-ui-00012-ht7` | `akretic-demo-ui-00011-cwb` |
| `akretic-root-orchestrator` | `akretic-root-orchestrator-00010-c5s` | `akretic-root-orchestrator-00009-xmz` |
| `akretic-policy-agent` | `akretic-policy-agent-00010-xxq` | `akretic-policy-agent-00009-xsr` |
| `akretic-knowledge-agent` | `akretic-knowledge-agent-00010-lpv` | `akretic-knowledge-agent-00009-lzz` |
| `akretic-research-agent` | `akretic-research-agent-00010-55l` | `akretic-research-agent-00009-rfm` |
| `akretic-approval-evidence` | `akretic-approval-evidence-00010-85n` | `akretic-approval-evidence-00009-hzt` |

Inspect revision history before any rollback:

```powershell
gcloud run revisions list --project akretic-a2a-trust-gateway --region us-central1 --service akretic-demo-ui
gcloud run revisions list --project akretic-a2a-trust-gateway --region us-central1 --service akretic-root-orchestrator
gcloud run revisions list --project akretic-a2a-trust-gateway --region us-central1 --service akretic-policy-agent
gcloud run revisions list --project akretic-a2a-trust-gateway --region us-central1 --service akretic-knowledge-agent
gcloud run revisions list --project akretic-a2a-trust-gateway --region us-central1 --service akretic-research-agent
gcloud run revisions list --project akretic-a2a-trust-gateway --region us-central1 --service akretic-approval-evidence
```

Rollback commands, approval required before execution:

```powershell
gcloud run services update-traffic akretic-demo-ui --project akretic-a2a-trust-gateway --region us-central1 --to-revisions akretic-demo-ui-00011-cwb=100
gcloud run services update-traffic akretic-root-orchestrator --project akretic-a2a-trust-gateway --region us-central1 --to-revisions akretic-root-orchestrator-00009-xmz=100
gcloud run services update-traffic akretic-policy-agent --project akretic-a2a-trust-gateway --region us-central1 --to-revisions akretic-policy-agent-00009-xsr=100
gcloud run services update-traffic akretic-knowledge-agent --project akretic-a2a-trust-gateway --region us-central1 --to-revisions akretic-knowledge-agent-00009-lzz=100
gcloud run services update-traffic akretic-research-agent --project akretic-a2a-trust-gateway --region us-central1 --to-revisions akretic-research-agent-00009-rfm=100
gcloud run services update-traffic akretic-approval-evidence --project akretic-a2a-trust-gateway --region us-central1 --to-revisions akretic-approval-evidence-00009-hzt=100
```

After any approved rollback, run:

```powershell
.\scripts\verify_cloudrun_config.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```
