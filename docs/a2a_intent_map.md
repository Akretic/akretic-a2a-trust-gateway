# A2A Intent Map

This map is the public-safe proof table for the VendorNova demo path. The same
fields appear in the Cloud Run result page and in evidence event metadata.

| Agent Card URL | agent | skill/intent | caller/callee | correlation_id | outcome | evidence event |
|---|---|---|---|---|---|---|
| `/.well-known/agent-card.json` on Policy Agent | `akretic-policy-agent` | `authorize_intent` | `root_orchestrator -> akretic-policy-agent` | `corr_*` | `allow` for internal retrieval | `a2a_call` event ID and hash |
| `/.well-known/agent-card.json` on Knowledge Agent | `akretic-knowledge-agent` | `retrieve_permitted_context` | `root_orchestrator -> akretic-knowledge-agent` | `corr_*` | permitted chunks plus denied source IDs | `a2a_call` event ID and hash |
| `/.well-known/agent-card.json` on Policy Agent | `akretic-policy-agent` | `authorize_intent` | `root_orchestrator -> akretic-policy-agent` | `corr_*` | `approval_required` for external export | `a2a_call` event ID and hash |
| `/.well-known/agent-card.json` on Approval/Evidence Agent | `akretic-approval-evidence-agent` | `request_approval` | `root_orchestrator -> akretic-approval-evidence-agent` | `corr_*` | pending approval request | `a2a_call` event ID and hash |

## Protocol Proof Boundary

- Agent Cards include `supportedInterfaces`, `securitySchemes`,
  `defaultInputModes`, `defaultOutputModes`, and explicit skills.
- Cards are validated locally with `a2a-sdk` while retaining the existing HTTP
  endpoints used by the demo.
- A2A call evidence includes caller, callee, skill/intent, Agent Card URL,
  `correlation_id`, evidence event ID, and event hash.
- A2A discovery and skill calls do not decide authorization. Gate0-lite remains
  the policy decision point.
