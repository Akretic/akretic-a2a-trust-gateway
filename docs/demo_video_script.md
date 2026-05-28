# Demo Video Script

Target length: 90 seconds. Hosted video URL only; do not commit or package raw
video exports.

| Time | Screen/action | Narration |
|---|---|---|
| 0:00-0:10 | Public Cloud Run home | "Akretic A2A Trust Gateway is a challenge prototype for controlled enterprise agent collaboration over A2A." |
| 0:10-0:20 | Start VendorNova review | "The demo uses synthetic VendorNova data and a procurement user persona." |
| 0:20-0:35 | Review proof row and model panel | "The root orchestrator uses Vertex/Gemini summarization, but policy, retrieval filtering, approvals, and evidence stay outside the model." |
| 0:35-0:50 | Permitted and denied sources | "RAG DMZ-lite gives Gemini only permitted context. Denied source IDs are visible as proof, but denied text is blocked before model context." |
| 0:50-1:05 | Approval panel | "Sensitive external action returns `approval_required`, so the export is paused until a reviewer decides." |
| 1:05-1:20 | A2A Proof and evidence proof | "A2A proof shows Agent Card resolution, skill calls, correlation IDs, and outcomes. Evidence verification shows a valid hash chain." |
| 1:20-1:30 | Reviewer decision / closing | "The point is controlled collaboration: agents can work together while authorization, approvals, and evidence remain enforceable outside Gemini." |

## Must Show

- Public URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
- Challenge prototype and synthetic-data labels.
- `Mode: vertex`, `Model: gemini-2.5-flash`, project, and region.
- `Denied before model context: executive_acquisition_memo.`
- `approval_required` gate.
- A2A proof with agent, skill, and `correlation_id`.
- Evidence proof with valid hash chain.
