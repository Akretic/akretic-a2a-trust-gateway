# Demo Video Script

Target length: 90 seconds. Hosted video URL only; do not commit or package raw
video exports.

| Time | Screen/action | Narration |
|---|---|---|
| 0:00-0:15 | Public Cloud Run home | "Agents can collaborate, but the model cannot decide what it may read, share, approve, or export. Akretic is a trust gateway/control plane for A2A enterprise agents." |
| 0:15-0:25 | Start VendorNova review | "The demo uses synthetic VendorNova data for a procurement and security vendor-risk workflow." |
| 0:25-0:40 | Review proof row and model panel | "The root entrypoint uses a Google ADK Workflow wrapper and Vertex/Gemini summarization, but policy, retrieval filtering, approvals, and evidence stay outside the model." |
| 0:40-0:55 | Permitted and denied sources | "RAG DMZ-lite gives Gemini only permitted context. Denied source IDs are visible as proof, but denied text is blocked before model context." |
| 0:55-1:08 | Approval panel | "Sensitive external action returns `approval_required`, so the export is paused until a reviewer decides." |
| 1:08-1:20 | A2A Proof and evidence proof | "A2A proof shows Agent Card URLs, agents, skill intents, caller and callee, correlation IDs, outcomes, and evidence event hashes. Evidence verification shows a valid hash chain." |
| 1:20-1:30 | Reviewer decision / closing | "The point is controlled collaboration: agents can work together while authorization, approvals, and evidence remain enforceable outside Gemini." |

## Must Show

- Public URL: `https://akretic-demo-ui-oes3slkexq-uc.a.run.app`
- Challenge prototype and synthetic-data labels.
- `Mode: vertex`, `Model: gemini-2.5-flash`, project, and region.
- `Denied before model context: executive_acquisition_memo.`
- `approval_required` gate.
- ADK wrapper proof.
- A2A proof with Agent Card URL, agent, skill/intent, caller/callee,
  `correlation_id`, outcome, and evidence event/hash.
- Evidence proof with valid hash chain.
