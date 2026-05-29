# Submission Package

## Submission Target

- Program: Google for Startups AI Agents Challenge
- Track: Track 3
- Product: Akretic A2A Trust Gateway
- Demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

## Current Status

P0, P1, P2, P3, and P4 are cleared. P5 submission packaging has a hosted demo
video URL recorded in `dist/video_url.txt`; final P5 acceptance remains pending
the final verifier set and acceptance tag. The proof path is deployed and
verified with public unauthenticated Cloud Run access to the demo UI. Private
agent/root/evidence services remain protected by Cloud Run IAM and are invoked
by the UI runtime service account.

## Prepared Deliverables

| Deliverable | Status | Artifact |
|---|---|---|
| Public Cloud Run demo URL | Ready | `https://akretic-demo-ui-oes3slkexq-uc.a.run.app` |
| README with install, test, and deploy instructions | Prepared | `README.md`, `docs/deployment.md` |
| Submission checklist | Prepared | `docs/submission_checklist.md` |
| 1-2 minute demo video script | Prepared | `docs/demo_video_script.md` |
| Demo video shot list | Prepared | `docs/video_shot_list.md` |
| Hosted video URL | Recorded | `dist/video_url.txt` |
| Devpost/submission answers | Prepared | `docs/submission_answers_public.md` |
| Devpost-ready answers | Prepared | `docs/devpost_answers.md` |
| Paste-ready form packet | Prepared | `docs/submission_form_packet.md` |
| Architecture diagram | Prepared | `docs/architecture.md`, `output/architecture/akretic-a2a-architecture.png` |
| Sample evidence report | Refreshed in P5 | latest `artifacts/sample-evidence-report-<run_id>.json` |
| Screenshots | Refreshed in P5 | `artifacts/screenshots/demo-home.png`, `artifacts/screenshots/demo-review-result.png`, `artifacts/screenshots/evidence-report.png` |
| Public-safe brief/PDF | Refreshed in P5 | `docs/public_brief.md`, `dist/akretic-a2a-trust-gateway-public-brief.pdf` |
| Final zip | Built in P5 | `dist/akretic-a2a-trust-gateway-submission.zip` |
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
- The current proof path uses Vertex/Gemini summarization and thin A2A Agent
  Card skill-call wiring, with ADK alignment documented as part of the Google
  Cloud agent architecture path rather than overclaiming full ADK-native
  orchestration.

## Package Rules

- Do not include raw `.mp4`, `.mov`, `.webm`, or other video exports in the repo
  or final zip.
- Do not include editing project files in the repo or final zip.
- Use a hosted video URL and record it in `dist/video_url.txt` after upload.
- Keep the attachment-style zip under 35 MB unless the live submission form says
  otherwise.
- Check the live submission form before final upload for current requirements.

## Final Verification

```powershell
.\scripts\verify_judge_readiness.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
.\scripts\verify_cloudrun_config.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic -KeepReport
```

## Manual Finalization Needed

- Paste or adapt `docs/devpost_answers.md` into the submission form.
- Attach the screenshots, sample evidence report, architecture doc, and public
  brief/PDF as the submission platform allows.
- Run the final verifier set and create the P5 acceptance tag only after it is
  green.
- Optional: add an `environment` project tag in Google Cloud if the Akretic
  organization later requires it for project hygiene.
