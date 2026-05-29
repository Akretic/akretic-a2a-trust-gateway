# P6 Acceptance - ADK Alignment Hardening

P6 can be considered for merge only when the ADK alignment wrapper and docs
strengthen the Google agent-platform story without changing P0-P5 trust
semantics. Final remediation puts the public root entrypoint through the wrapper
and keeps the verified proof path delegated to the same orchestrator.

## Acceptance Checks

- Branch is `p6/adk-alignment` and remains isolated until review.
- The verified root orchestrator path is not replaced.
- Public Cloud Run demo behavior shows wrapper proof only after the wrapper is
  actually in the runtime path.
- `agents/root_orchestrator/adk_alignment.py` delegates to
  `run_vendor_review_workflow`.
- ADK alignment docs map the current root workflow to agent/tool/model/approval
  and trace concepts without claiming full ADK-native orchestration.
- Tests prove the wrapper does not bypass derived identity.
- Tests prove Gate0-lite remains the policy decision point.
- Tests prove RAG DMZ-lite filters denied text before model context.
- Tests prove `approval_required` remains enforced before sensitive external
  action completion.
- Tests prove evidence logging and verification remain in the path.
- Tests prove A2A Agent Card / skill-call proof remains visible with Agent Card
  URL, agent, skill/intent, caller/callee, `correlation_id`, outcome, and
  evidence event/hash.
- Denied source IDs may appear as proof, but denied source text does not enter
  Gemini prompt, output, UI, logs, evidence reports, or public samples.
- No Agent Runtime, Agent Registry, Firestore, embeddings, Google Search
  grounding, new data sources, new workflows, new public routes, broad IAM, or
  new Cloud Run resource classes are introduced.
- No P5 package artifacts are changed unless explicitly assigned.

## Required Verification

Run from `p6/adk-alignment` before requesting merge review:

```powershell
.\scripts\verify_judge_readiness.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\deploy_cloudrun.ps1 -PreflightOnly
.\scripts\verify_cloudrun_config.ps1
.\scripts\verify_cloudrun_p0.ps1 -RequirePublic
```

P6 should not be merged unless all commands pass and the diff shows no P0-P5
regression, public overclaim, runtime replacement, new cloud resource class, or
private service exposure.
