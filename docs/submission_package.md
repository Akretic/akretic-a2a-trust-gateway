# Submission Package

## Submission Target

- Program: Google for Startups AI Agents Challenge
- Track: Track 3
- Product: Akretic A2A Trust Gateway
- Demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

## Current Status

The P0 proof path is deployed and verified with public unauthenticated Cloud Run
access to the demo UI. Private agent/root/evidence services remain protected by
Cloud Run IAM and are invoked by the UI runtime service account.

## Prepared Deliverables

| Deliverable | Status | Artifact |
|---|---|---|
| Public Cloud Run demo URL | Ready | `https://akretic-demo-ui-oes3slkexq-uc.a.run.app` |
| README with install, test, and deploy instructions | Prepared | `README.md`, `docs/deployment.md` |
| Submission checklist | Prepared | `docs/submission_checklist.md` |
| 1-2 minute demo video script | Prepared | `docs/demo_script.md` |
| Raw silent demo walkthrough | Prepared locally | `output/playwright/video/akretic-p0-demo-raw.webm` |
| Devpost/submission answers | Prepared | `docs/submission_answers_public.md` |
| Architecture diagram | Prepared | `docs/architecture.md` |
| Sample evidence report | Prepared | `artifacts/sample-evidence-report-run_be30e4f10ef7483d9f6695fd64d5dfa3.json` |
| Screenshots | Prepared from authenticated Cloud Run HTML capture | `output/playwright/demo-home.png`, `output/playwright/demo-review-result.png` |
| Public-safe brief/PDF | Prepared | `docs/public_brief.md`, `output/pdf/akretic-a2a-trust-gateway-public-brief.pdf` |
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

## Final Verification

```powershell
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

## Manual Finalization Needed

- Add the GitHub remote and push after a repository URL is available.
- Record and upload the 1-2 minute demo video using `docs/demo_script.md`.
- Paste or adapt `docs/submission_answers_public.md` into the submission form.
- Attach the screenshots, sample evidence report, architecture doc, and public
  brief/PDF as the submission platform allows.
- Optional: add an `environment` project tag in Google Cloud if the Akretic
  organization later requires it for project hygiene.
