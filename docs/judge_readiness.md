# Judge Readiness

Use this checklist to verify the public challenge path without changing product
scope or deployment shape.

Public URL:

```text
https://akretic-demo-ui-oes3slkexq-uc.a.run.app/
```

## 90-Second Path

1. Open the public URL and confirm the page is labeled as a challenge prototype using synthetic data.
2. Keep persona as `procurement_user` and start the VendorNova review.
3. Confirm the proof row shows Identity, Policy, RAG Filter, A2A, Approval, and Evidence Verify.
4. Confirm Vertex mode is visible: `Mode: vertex`, `Model: gemini-2.5-flash`, project `akretic-a2a-trust-gateway`, location `us-central1`.
5. Confirm permitted source IDs are listed.
6. Confirm `executive_acquisition_memo` is shown only as a denied source ID before model context.
7. Confirm the external action is `approval_required` and export status remains blocked pending approval.
8. Confirm ADK wrapper proof shows the root Workflow delegates to the verified orchestrator.
9. Confirm A2A proof shows Agent Card URL, agent, skill/intent, caller/callee,
   `correlation_id`, outcome, and evidence event/hash.
10. Record the reviewer decision as `security_reviewer`.
11. Confirm evidence verification reports a valid hash chain.

## Trust Boundary

- Gemini summarizes only permitted synthetic context.
- Gemini does not decide identity, policy, retrieval access, approval state, action completion, or evidence validity.
- Gate0-lite decides policy.
- RAG DMZ-lite filters restricted source text before model context is assembled.
- Denied source IDs may appear as proof, but denied source text must not enter model input, UI output, evidence reports, logs, or public samples.
- `approval_required` pauses sensitive side effects until reviewer decision.
- Evidence ledger verification proves the demo run's event chain.
- The Google ADK Workflow wrapper delegates to the verified orchestrator path.
- A2A proof shows collaboration through Agent Cards and skill-call evidence.

## Automated Check

Run:

```powershell
.\scripts\verify_judge_readiness.ps1
```

Expected result:

- public home page returns HTTP 200;
- VendorNova review starts from the UI;
- Vertex mode is visible;
- denied source ID proof is visible without denied text;
- approval gate is visible;
- ADK wrapper proof is visible;
- A2A proof is visible;
- evidence verification is visible;
- sample evidence report is valid.

## Claim Boundary

Use bounded language: policy-mediated, approval-gated, tamper-evident,
permission-preserving for this synthetic corpus, and challenge prototype.

Do not imply launch approval, legal/compliance status, Marketplace status,
complete autonomy for enterprise actions, or universal safety.
