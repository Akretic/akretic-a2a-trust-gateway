# P0 Acceptance Criteria

## Required tests

| Test | Expected result |
|---|---|
| `test_identity_spoofing` | Request body claiming admin groups is ignored; server/session/demo identity wins |
| `test_policy_decisions` | Policy evaluator returns deterministic `allow`, `deny`, and `approval_required` outcomes |
| `test_rag_filtering` | Restricted executive memo is excluded from prompt/context for demo users |
| `test_a2a_cards` | Policy and Knowledge agents serve valid Agent Cards |
| `test_a2a_remote_call_logged` | Root remote call logs caller, callee, skill, and correlation ID |
| `test_approval_gate` | External-facing exception action pauses until reviewer approve/reject is recorded |
| `test_evidence_verify` | Verify endpoint detects valid and tampered event chains |
| `test_evidence_report` | Evidence report includes A2A calls, retrieval allow/deny, approval, reviewer decision, and verification |
| `test_gemini_context` | Gemini prompt builder excludes denied document contents and records the model path |
| `test_demo_ui_root_call` | Demo UI calls the deployed root service when configured and uses Cloud Run auth headers for private approval/evidence calls |
| `test_claims_public_copy` | Public copy excludes banned overclaims |

## Evidence required for final demo

- Run ID visible in UI.
- Policy decision log for allowed retrieval.
- Policy denial for executive memo retrieval.
- Proof that denied content is not in model context.
- `approval_required` record for sensitive side effect.
- Reviewer approval/rejection record.
- Hash-chain verification result.
- Downloadable evidence report.

## Stop-ship conditions

- Any restricted chunk reaches prompt/model context for unauthorized persona.
- Request-body privilege claims can upgrade identity.
- Demo-critical route silently uses stubbed data without explicit label/evidence.
- Public copy claims production certification, guaranteed compliance, Marketplace approval, or universal safety.
- Evidence verify endpoint cannot detect tampering.
