# Submission Package

## Submission Target

- Program: Google for Startups AI Agents Challenge
- Track: Track 3
- Product: Akretic A2A Trust Gateway
- Demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`

## Current Status

P0, P1, P2, P3, P4, and P5 are cleared. P5 submission packaging has a hosted
demo video URL recorded in `dist/video_url.txt`, a rebuilt final zip, and an
unlisted Akretic landing page at `https://akretic.com/a2a-trust-gateway-demo`.
The proof path is deployed and verified with public unauthenticated Cloud Run
access to the demo UI, and the GitHub repository is public/judge-accessible.
Private agent/root/evidence services remain protected by Cloud Run IAM and are
invoked by the UI runtime service account.

Final challenge-readiness remediation is complete for the declared prototype
scope. The latest AuditOps report is A/90 with quality gate passed, 0 active
caps, 0 findings, and 0 P0/P1 tasks. The remediation added repeatable JUnit,
package-build, and public-surface SARIF evidence without changing the verified
trust semantics.

## Prepared Deliverables

| Deliverable | Status | Artifact |
|---|---|---|
| Public Cloud Run demo URL | Ready | `https://akretic-demo-ui-oes3slkexq-uc.a.run.app` |
| Unlisted Akretic landing page | Ready | `https://akretic.com/a2a-trust-gateway-demo` |
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
| A2A intent map | Prepared | `docs/a2a_intent_map.md` |
| ADK alignment proof | Prepared | `docs/adk_alignment.md` |
| Third-party rights disclosure | Prepared | `docs/third_party_rights.md` |
| Original-work eligibility note | Prepared | `docs/eligibility_statement.md` |
| Final zip | Built in P5 | `dist/akretic-a2a-trust-gateway-submission.zip` |
| Final readiness remediation | Complete | `docs/challenge_readiness_remediation.md`, `.auditops/latest-audit-report.md` |
| Limitations and synthetic-data disclosure | Prepared | `docs/submission_answers_public.md`, `docs/public_claims_guardrails.md` |

## Demo Proof Points

- Root orchestrator calls Policy, Knowledge, and Approval/Evidence services over
  A2A Agent Card skill calls.
- Gate0-lite returns deterministic `allow`, `deny`, and `approval_required`.
- RAG DMZ-lite filters restricted source contents before Gemini context.
- Vertex AI Gemini summarizes only permitted context.
- Sensitive external export returns `approval_required`.
- Reviewer decision is recorded by `security_reviewer`.
- Evidence report verifies the hash chain and includes material decisions.
- The current proof path uses Vertex/Gemini summarization, A2A Agent Card
  skill-call wiring, and a Google ADK Workflow wrapper that delegates to the
  verified orchestrator path.

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
- Optional: add an `environment` project tag in Google Cloud if the Akretic
  organization later requires it for project hygiene.
