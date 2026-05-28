# Google Tools Harness Plan

## Required for P0

| Tool | Use in this build | P0 notes |
|---|---|---|
| Google Cloud Project | Single project for challenge demo | Create early; keep region consistent |
| Vertex AI / Gemini | Model path for root orchestrator summarization | Gemini may summarize permitted context only; it does not authorize |
| Google ADK | Root orchestrator framework and agent development path | Integrate after deterministic controls are green |
| A2A / Agent Cards | Remote Policy and Knowledge agents are discoverable and callable | Expose both `/agent-card.json` and `/.well-known/agent-card.json` |
| Cloud Run | Deploy all P0 services | Cloud Run first; public judge URL must stay live |
| Artifact Registry | Store container images | Prefer regional Docker repository |
| Cloud Build or `gcloud run deploy --source` | Build and deploy services | Use whichever is fastest and reliable |
| Cloud Storage | Store synthetic corpus exports and evidence reports | Local JSONL can remain dev default |
| Cloud Logging | Runtime visibility and run_id troubleshooting | Log `run_id`, `actor_id`, `agent_id`, `skill`, `outcome` |
| Cloud Trace | Cross-service traceability | Enable after Cloud Run path works |
| IAM / Service Accounts | Least-privilege service execution | Separate runtime service account if possible |
| Secret Manager | Store runtime secrets and config values | Do not commit credentials |

## Stretch only after P0

| Tool | Stretch use |
|---|---|
| Agent Runtime | Managed agent deployment once Cloud Run P0 is stable |
| Agent Registry / Gemini Enterprise A2A registration | Register custom A2A agent if time permits |
| Firestore | Durable approval/evidence state beyond local JSONL/Cloud Storage |
| Vertex AI Embeddings | Replace in-memory lexical retrieval with embeddings |
| Google Search grounding | Controlled public research from allowlisted sources |

## Do not spend time on before P0

- GKE.
- Full enterprise SSO.
- Real enterprise data connectors.
- Marketplace packaging.
- Multi-tenant policy console.
- Production compliance hardening.

## Setup checklist

```bash
export PROJECT_ID="akretic-a2a-demo"
export REGION="us-central1"

gcloud auth login
gcloud config set project "$PROJECT_ID"

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  cloudtrace.googleapis.com \
  secretmanager.googleapis.com

gcloud artifacts repositories create akretic \
  --repository-format=docker \
  --location="$REGION" \
  --description="Akretic challenge prototype containers"
```

## Service map

| Service | Default local port | Cloud Run service name |
|---|---:|---|
| Demo UI | 8080 | `akretic-demo-ui` |
| Root Orchestrator | 8100 | `akretic-root-orchestrator` |
| Policy Agent | 8101 | `akretic-policy-agent` |
| Knowledge Agent | 8102 | `akretic-knowledge-agent` |
| Research Agent | 8103 | `akretic-research-agent` |
| Approval/Evidence Agent | 8104 | `akretic-approval-evidence` |

## Environment variables

```bash
PROJECT_ID=
REGION=us-central1
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash
AKRETIC_ENV=dev
AKRETIC_DEMO_PERSONA=procurement_user
EVIDENCE_DIR=.akretic/evidence
CORPUS_DIR=corpus
POLICY_PATH=policies/policy.yaml
PERSONAS_PATH=policies/personas.yaml
```
