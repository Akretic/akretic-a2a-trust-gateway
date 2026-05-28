# Submission Package

## Submission Target

- Program: Google for Startups AI Agents Challenge
- Track: Track 3
- Product: Akretic A2A Trust Gateway
- Demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

## Current Status

The P0 proof path is deployed and verified with authenticated Cloud Run access.
Public unauthenticated access is still blocked by the Akretic organization policy
for `allUsers` IAM bindings. See `docs/deployment_notes.md`.

## Prepared Deliverables

| Deliverable | Status | Artifact |
|---|---|---|
| Public Cloud Run demo URL | Blocked by org policy | `https://akretic-demo-ui-oes3slkexq-uc.a.run.app` |
| README with install, test, and deploy instructions | Prepared | `README.md`, `docs/deployment.md` |
| 1-2 minute demo video script | Prepared | `docs/demo_script.md` |
| Devpost/submission answers | Prepared | `docs/submission_answers_public.md` |
| Architecture diagram | Prepared | `docs/architecture.md` |
| Sample evidence report | Prepared | `artifacts/sample-evidence-report-run_9e24c7f1d4d0452989c0e39c0e48a4c1.json` |
| Screenshots | Prepared from authenticated Cloud Run HTML capture | `output/playwright/demo-home.png`, `output/playwright/demo-review-result.png` |
| Public-safe brief/PDF | Optional stretch | TBD |
| Limitations and synthetic-data disclosure | Prepared | `docs/submission_answers_public.md`, `docs/public_claims_guardrails.md` |

## Demo Proof Points

- Root orchestrator calls Policy, Knowledge, and Approval/Evidence services over
  A2A-style HTTP with Agent Cards.
- Gate0-lite returns deterministic `allow`, `deny`, and `approval_required`.
- RAG DMZ-lite filters restricted source contents before Gemini context.
- Vertex AI Gemini summarizes only permitted context.
- Sensitive external export returns `approval_required`.
- Reviewer decision is recorded by `security_reviewer`.
- Evidence report verifies the hash chain and includes material decisions.

## Manual Action Required

Allow this binding on the demo UI service:

```powershell
gcloud run services add-iam-policy-binding akretic-demo-ui `
  --project akretic-a2a-trust-gateway `
  --region us-central1 `
  --member allUsers `
  --role roles/run.invoker
```

The current error is:

```text
FAILED_PRECONDITION: One or more users named in the policy do not belong to a permitted customer, perhaps due to an organization policy.
```
