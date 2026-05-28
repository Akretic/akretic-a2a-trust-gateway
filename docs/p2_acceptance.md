# P2 Acceptance - Gemini/Vertex Hardening

P2 is accepted when the approved Vertex AI Gemini path is easier to prove, operate, and troubleshoot without changing the trust boundary.

## Acceptance Checks

- Public demo still uses the Cloud Run root orchestrator and private agent services.
- Root orchestrator runs with `AKRETIC_GEMINI_MODE=vertex` in Cloud Run.
- UI clearly shows the Vertex/Gemini summarization path when the public demo is healthy.
- Evidence records the model mode, model name, service path, permitted source IDs, and denied source IDs.
- Tests prove denied source contents do not enter the Gemini prompt.
- Tests prove request-body identity claims cannot expand model context.
- Gemini summary may use permitted context only and must not decide authorization.
- Gemini summary must not claim an approval-gated export/action completed while it is still pending.
- Gemini unavailable, bad mode, or missing project configuration returns a clear failure state.
- Gate0-lite remains the only policy decision point.
- RAG DMZ-lite still filters before context reaches Gemini.
- README or deployment docs list the required Vertex/Gemini environment variables without secret values.
- `pytest -q` passes.
- `scripts/verify_cloudrun_p0.ps1 -RequirePublic` passes after any Cloud Run redeploy.

## Scope Boundary

P2 is hardening, not platform expansion. Do not add ADK-native, Agent Runtime, embeddings, search grounding, or new workflows unless P2 acceptance is already green and the user explicitly assigns that stretch work.

Recommended branch: `p2/gemini-vertex-hardening`.
