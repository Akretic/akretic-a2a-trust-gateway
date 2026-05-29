# P5 Acceptance - Submission Package

P5 is accepted when the final public submission package matches the running
Cloud Run demo, contains only public-safe artifacts, and avoids new product
scope.

## Acceptance Checks

- P0, P1, P2, P3, and P4 remain cleared.
- P5 submission package is accepted and preserved.
- Final package exists at `dist/akretic-a2a-trust-gateway-submission.zip`.
- Final package is under 35 MB.
- Final package contains no raw video files, screen recordings, editing project
  files, or large video exports.
- Hosted video URL is tracked in `dist/video_url.txt`.
- Demo video planning material is source-only:
  - `docs/demo_video_script.md`
  - `docs/video_shot_list.md`
- Fresh public-safe PDF exists at
  `dist/akretic-a2a-trust-gateway-public-brief.pdf`.
- Public brief source remains `docs/public_brief.md`.
- Devpost-ready public answers exist at `docs/devpost_answers.md`.
- Submission checklist and package docs match the current Cloud Run URL,
  synthetic-data posture, Vertex/Gemini path, and no-video-binary rule.
- Fresh sample evidence report exists under `artifacts/`.
- Fresh screenshots exist under `artifacts/screenshots/`:
  - `demo-home.png`
  - `demo-review-result.png`
  - `evidence-report.png`
- Public copy remains bounded and does not imply production launch approval,
  legal or compliance status, Marketplace listing, or universal safety.
- The current proof path is described as Vertex/Gemini summarization, A2A Agent
  Card skill-call wiring, and a Google ADK Workflow wrapper that delegates to
  the verified orchestrator path.

## Final Verification

Run from `main` before P5 acceptance:

```powershell
.\scripts\verify_judge_readiness.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
.\scripts\verify_cloudrun_config.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic -KeepReport
```

Before final upload, check the live submission form for current attachment,
file-size, file-type, and hosted-video URL requirements.
