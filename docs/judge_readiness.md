# Judge Readiness

Use this checklist to verify the public challenge path without changing product
scope or deployment shape.

Public URL:

```text
https://akretic-demo-ui-oes3slkexq-uc.a.run.app/
```

## 2-Minute Path

1. Open the public URL and confirm the page is labeled as a challenge prototype using synthetic data.
2. Keep persona as `procurement_user` and start the VendorNova review.
3. Confirm the Judge Proof panel shows service path, Vertex Gemini mode, A2A Agent Cards, denied executive memo, `approval_required`, reviewer path pending, and valid hash chain.
4. Confirm Vertex mode is visible: `Mode: vertex`, `Model: gemini-2.5-flash`, project `akretic-a2a-trust-gateway`, location `us-central1`.
5. Confirm permitted source IDs and Research Agent seeded public source IDs/citations are listed.
6. Confirm `executive_acquisition_memo` is shown only as a denied source ID before model context.
7. Confirm the external action is `approval_required` and no external egress is presented as complete.
8. Confirm A2A proof shows agent, skill, base URL, Agent Card resolution, HTTP status/latency, request/response hashes, event hash, and `correlation_id`.
9. Open the current-run evidence report for that exact `run_id` and confirm it shows viewer persona and identity source.
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
- A2A proof shows collaboration through the Agent Card / skill-call adapter.
- Research Agent participation is a real in-path A2A call using seeded allowlisted public snippets.
- Evidence/verify UI routes require a demo viewer role in cloud mode.

## Automated Check

Run:

```powershell
.\.venv\Scripts\python.exe scripts\p0_verify.py --base-url https://<PUBLIC_DEMO_URL> --mode cloud --root-url https://<ROOT_SERVICE_URL> --policy-url https://<POLICY_SERVICE_URL> --knowledge-url https://<KNOWLEDGE_SERVICE_URL> --research-url https://<RESEARCH_SERVICE_URL> --approval-url https://<APPROVAL_EVIDENCE_SERVICE_URL> --expect-vertex --fail-on-local
.\.venv\Scripts\python.exe scripts\make_final_handoff.py --mode cloud --base-url https://<PUBLIC_DEMO_URL> --root-url https://<ROOT_SERVICE_URL> --policy-url https://<POLICY_SERVICE_URL> --knowledge-url https://<KNOWLEDGE_SERVICE_URL> --research-url https://<RESEARCH_SERVICE_URL> --approval-url https://<APPROVAL_EVIDENCE_SERVICE_URL> --project-label <PROJECT_OR_REDACTED_PROJECT_LABEL> --demo-ui-revision <DEMO_UI_REVISION> --root-revision <ROOT_REVISION> --policy-revision <POLICY_REVISION> --knowledge-revision <KNOWLEDGE_REVISION> --research-revision <RESEARCH_REVISION> --approval-revision <APPROVAL_REVISION>
.\scripts\verify_judge_readiness.ps1
```

Expected result:

- public home page returns HTTP 200;
- VendorNova review starts from the UI;
- Vertex mode is visible;
- denied source ID proof is visible without denied text;
- approval gate is visible;
- Research Agent proof is visible;
- A2A proof is visible with transport hashes;
- evidence verification is visible;
- current-run evidence report `run_id` matches the active run and verifies.

## Claim Boundary

Use bounded language: policy-mediated, approval-gated, tamper-evident,
permission-preserving for this synthetic corpus, and challenge prototype.

Do not imply launch approval, legal/compliance status, Marketplace status,
complete autonomy for enterprise actions, or universal safety.
