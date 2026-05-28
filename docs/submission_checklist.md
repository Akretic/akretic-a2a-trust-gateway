# P0 Submission Checklist

## Fixed Submission Values

- Product name: Akretic A2A Trust Gateway
- Program: Google for Startups AI Agents Challenge
- Track: Track 3
- Public demo URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
- Google Cloud project: `akretic-a2a-trust-gateway`
- Region: `us-central1`
- Runtime: Cloud Run
- Model path: Vertex AI Gemini
- Data posture: synthetic challenge corpus only

## Attach Or Reference

- README: `README.md`
- Deployment notes: `docs/deployment_notes.md`
- Architecture: `docs/architecture.md`
- Demo script: `docs/demo_script.md`
- Public-safe submission answers: `docs/submission_answers_public.md`
- Public brief: `docs/public_brief.md`
- Public brief PDF: `output/pdf/akretic-a2a-trust-gateway-public-brief.pdf`
- Sample evidence report: `artifacts/sample-evidence-report-run_be30e4f10ef7483d9f6695fd64d5dfa3.json`
- Screenshots:
  - `output/playwright/demo-home.png`
  - `output/playwright/demo-review-result.png`
- Optional raw walkthrough capture:
  - `output/playwright/video/akretic-p0-demo-raw.webm`
  - `output/playwright/video/akretic-p0-demo-raw.metadata.json`

## Verified P0 Proof

- Agents coordinate through A2A-style HTTP calls and Agent Cards.
- Gate0-lite returns deterministic `allow`, `deny`, and `approval_required`.
- RAG DMZ-lite filters restricted synthetic documents before Gemini context.
- Vertex AI Gemini receives permitted context only.
- Sensitive external export pauses on `approval_required`.
- Reviewer decision is recorded by the Approval/Evidence Agent.
- Evidence report verifies the hash chain.
- Public copy avoids production, certification, compliance, and universal-safety overclaims.

## Manual Steps

1. Create or provide the GitHub repository URL.
2. Add the remote and push `main`.
3. Record or upload the 1-2 minute demo video from the public Cloud Run URL.
   The optional raw silent walkthrough can be generated with
   `.\.venv\Scripts\python.exe .\scripts\record_demo_video.py`.
4. Paste `docs/submission_answers_public.md` into the submission form.
5. Upload or link the screenshots, evidence report, architecture material, and public brief/PDF.
6. Optional: add the Google Cloud `environment` project tag if Akretic org policy requires it.

## Final Smoke Command

```powershell
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```
