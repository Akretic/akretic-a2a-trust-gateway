# P2 Acceptance - Gemini/Vertex Hardening

P2 is accepted when the approved Vertex AI Gemini path is easier to prove, operate, and troubleshoot without changing the trust boundary.

Status: complete as of the 2026-05-28 P2 Cloud Run verification recorded in
`docs/deployment_notes.md`.

## Acceptance Checks

- Cloud Run demo uses `AKRETIC_GEMINI_MODE=vertex`, not local mode.
- Cloud Run root service uses `GOOGLE_CLOUD_PROJECT=akretic-a2a-trust-gateway`.
- Cloud Run root service uses `GOOGLE_CLOUD_LOCATION=us-central1`.
- Cloud Run root service uses `VERTEX_MODEL=gemini-2.5-flash`.
- UI clearly shows whether the run used Vertex/Gemini or local test mode.
- Evidence records the model path and mode used, including service path, model, project, location, prompt hash, permitted source IDs, and denied source IDs.
- Gemini receives only permitted context.
- Denied source IDs may appear as proof, but denied source text never enters the prompt, model context, UI, evidence report, or output.
- Tests or assertions prove `executive_acquisition_memo` content is absent from Gemini input and output for non-executive personas.
- README explains exactly what Gemini does and does not decide.
- Failure handling is clear for Vertex auth, quota, model, API, credential, bad-mode, and missing-project errors.
- `pytest -q` passes.
- `scripts/verify_cloudrun_p0.ps1 -RequirePublic` passes after redeploy.

## Scope Boundary

P2 is hardening, not platform expansion. Do not add ADK-native, Agent Runtime, embeddings, search grounding, or new workflows unless P2 acceptance is already green and the user explicitly assigns that stretch work.

Recommended branch: `p2/gemini-vertex-hardening`.
