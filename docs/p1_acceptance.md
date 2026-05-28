# P1 Acceptance - Demo-Path Polish

P1 is accepted when the existing VendorNova judge path is easier to run and scan without expanding product scope.

## Acceptance Checks

- Public judge URL loads.
- VendorNova review starts from the UI.
- Review page shows `run_id`.
- Review page shows permitted sources.
- Review page shows `Denied before model context: executive_acquisition_memo.`
- Review page shows `approval_required` for the external/sensitive action.
- Reviewer approve/reject path is visible.
- Evidence verification result is visible.
- A2A calls show agent, skill, and `correlation_id`.
- Synthetic-data and challenge-prototype labels are visible.
- README includes a `90-second judge walkthrough`.
- `pytest -q` passes.
- `scripts/verify_cloudrun_p0.ps1 -RequirePublic` passes.

## Scope Boundary

P1 does not change the P0 trust semantics. Gate0-lite remains the policy decision point, RAG DMZ-lite filters before model context, approval remains required before sensitive external action completion, and the evidence ledger remains the proof source.
