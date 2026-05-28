# P5 Submission Checklist

## Fixed Submission Values

- Product name: Akretic A2A Trust Gateway
- Program: Google for Startups AI Agents Challenge
- Track: Track 3
- Public demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
- Private GitHub repository: `https://github.com/Akretic/akretic-a2a-trust-gateway`
- Google Cloud project: `akretic-a2a-trust-gateway`
- Region: `us-central1`
- Runtime: Cloud Run
- Model path: Vertex AI Gemini
- Data posture: synthetic challenge corpus only
- Video delivery: hosted video URL only; no video binaries in repo or zip
- Package size target: 35 MB maximum unless the live submission form says otherwise

## Attach Or Reference

- README: `README.md`
- Deployment notes: `docs/deployment_notes.md`
- Architecture: `docs/architecture.md`
- Architecture Mermaid source: `docs/architecture.mmd`
- Architecture images:
  - `output/architecture/akretic-a2a-architecture.svg`
  - `output/architecture/akretic-a2a-architecture.png`
- Demo video script: `docs/demo_video_script.md`
- Video shot list: `docs/video_shot_list.md`
- Hosted video URL: `dist/video_url.txt` after upload
- Public-safe submission answers: `docs/submission_answers_public.md`
- Paste-ready form packet: `docs/submission_form_packet.md`
- Devpost answers: `docs/devpost_answers.md`
- Public brief: `docs/public_brief.md`
- Public brief PDF: `dist/akretic-a2a-trust-gateway-public-brief.pdf`
- Sample evidence report: latest `artifacts/sample-evidence-report-<run_id>.json`
- Screenshots:
  - `artifacts/screenshots/demo-home.png`
  - `artifacts/screenshots/demo-review-result.png`
  - `artifacts/screenshots/evidence-report.png`
- Final package:
  - `dist/akretic-a2a-trust-gateway-submission.zip`

## Verified P0 Proof

- Agents coordinate through A2A-style HTTP calls and Agent Cards.
- Gate0-lite returns deterministic `allow`, `deny`, and `approval_required`.
- RAG DMZ-lite filters restricted synthetic documents before Gemini context.
- Vertex AI Gemini receives permitted context only.
- Sensitive external export pauses on `approval_required`.
- Reviewer decision is recorded by the Approval/Evidence Agent.
- Evidence report verifies the hash chain.
- Public copy avoids production, certification, compliance, and universal-safety overclaims.
- Challenge submission does not claim or imply a Google Cloud Marketplace listing.

## Manual Steps

1. GitHub repository created and `main` pushed.
2. P0-P5 work branches pushed for traceability.
3. Record and upload the 1-2 minute demo video to an external host.
4. Write the hosted video URL to `dist/video_url.txt`.
5. Paste `docs/devpost_answers.md` into the submission form.
6. Upload or link the screenshots, evidence report, architecture image, and public brief/PDF.
7. Check the live submission form before final upload for current file-size, file-type, and video URL requirements.

## Final Verification Commands

```powershell
.\scripts\verify_judge_readiness.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
.\scripts\verify_cloudrun_config.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic -KeepReport
```
