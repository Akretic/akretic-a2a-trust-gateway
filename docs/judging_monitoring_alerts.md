# Judging Monitoring Alerts

These policies are for the Akretic A2A Trust Gateway challenge prototype judging
window. They are operational readiness checks, not production compliance claims.

## Recommended Alert Policies

- Cloud Run 5xx count greater than `0` during the judging window for `akretic-demo-ui`, `akretic-root-orchestrator`, `akretic-policy-agent`, `akretic-knowledge-agent`, `akretic-research-agent`, and `akretic-approval-evidence`.
- Root Orchestrator request latency greater than `30s`.
- Agent Card latency greater than `5s` for Policy, Knowledge, Research, and Approval/Evidence services.
- Vertex/Gemini failures or `429` spikes from structured events `vertex_429`, `vertex_5xx`, and `vertex_timeout`.
- Evidence invalid states from structured event `evidence_verify_invalid`.
- Forbidden-string scan findings from `forbidden-string-scan.json`.
- Readiness burn-in failure from `readiness-burnin-output.json` where `ok` is not `true`.

## Structured Log Event Names

The app emits JSON log records for:

- `a2a_card_timeout`
- `a2a_skill_timeout`
- `a2a_retry`
- `a2a_cache_hit`
- `a2a_cache_miss`
- `vertex_429`
- `vertex_5xx`
- `vertex_timeout`
- `evidence_write_conflict`
- `evidence_verify_invalid`
- `approval_conflict`
- `policy_receipt_invalid`
- `corpus_load_failure`

Log entries must contain metadata only. Restricted document text and restricted
test markers are not logged.
