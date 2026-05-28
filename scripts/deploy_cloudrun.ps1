param(
  [string]$ProjectId = "akretic-a2a-trust-gateway",
  [string]$Region = "us-central1",
  [string]$Repository = "akretic",
  [string]$ImageTag = "p0-latest",
  [string]$RuntimeServiceAccount = "akretic-p0-runtime",
  [string]$EvidenceBucket = "akretic-a2a-trust-gateway-evidence",
  [string]$ExpectedAccount = "sean.w@akretic.com",
  [switch]$PreflightOnly
)

$ErrorActionPreference = "Stop"

$AllowedProjectId = "akretic-a2a-trust-gateway"
$AllowedRegion = "us-central1"
$AllowedServices = @(
  "akretic-demo-ui",
  "akretic-root-orchestrator",
  "akretic-policy-agent",
  "akretic-knowledge-agent",
  "akretic-research-agent",
  "akretic-approval-evidence"
)

function Run-Step {
  param(
    [string]$Description,
    [string[]]$Command
  )
  Write-Host "`n==> $Description"
  Write-Host ($Command -join " ")
  $exe = $Command[0]
  $args = $Command[1..($Command.Length - 1)]
  & $exe @args
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code ${LASTEXITCODE}: $($Command -join ' ')"
  }
}

function Assert-Equal {
  param(
    [object]$Actual,
    [object]$Expected,
    [string]$Name
  )
  if ($Actual -ne $Expected) {
    throw "$Name was '$Actual', expected '$Expected'"
  }
}

function Test-DeploymentPreflight {
  Assert-Equal $ProjectId $AllowedProjectId "target project"
  Assert-Equal $Region $AllowedRegion "target region"
  foreach ($service in $AllowedServices) {
    if (-not $service.StartsWith("akretic-")) {
      throw "Service allowlist contains non-akretic service '$service'"
    }
  }

  $activeAccount = (& gcloud config get-value account).Trim()
  $activeProject = (& gcloud config get-value project).Trim()
  Assert-Equal $activeAccount $ExpectedAccount "active gcloud account"
  Assert-Equal $activeProject $ProjectId "active gcloud project"

  $billing = gcloud billing projects describe $ProjectId --format=json | ConvertFrom-Json
  if (-not [bool]$billing.billingEnabled) {
    throw "Billing is not enabled for $ProjectId"
  }

  return [ordered]@{
    project_id = $ProjectId
    region = $Region
    active_account = $activeAccount
    active_project = $activeProject
    billing_enabled = [bool]$billing.billingEnabled
    allowed_services = $AllowedServices
    runtime_service_account = "$RuntimeServiceAccount@$ProjectId.iam.gserviceaccount.com"
    evidence_bucket = $EvidenceBucket
  }
}

function Ensure-ServiceAccount {
  param([string]$Email)
  $existing = & gcloud iam service-accounts describe $Email --project $ProjectId --format "value(email)" 2>$null
  if (-not $existing) {
    Run-Step "Create runtime service account" @(
      "gcloud", "iam", "service-accounts", "create", $RuntimeServiceAccount,
      "--project", $ProjectId,
      "--display-name", "Akretic P0 Cloud Run runtime"
    )
  }
}

function Ensure-ArtifactRepo {
  $existing = & gcloud artifacts repositories describe $Repository --project $ProjectId --location $Region --format "value(name)" 2>$null
  if (-not $existing) {
    Run-Step "Create Artifact Registry repository" @(
      "gcloud", "artifacts", "repositories", "create", $Repository,
      "--project", $ProjectId,
      "--repository-format", "docker",
      "--location", $Region,
      "--description", "Akretic A2A Trust Gateway P0 containers"
    )
  }
}

function Ensure-Bucket {
  $existing = & gcloud storage buckets describe "gs://$EvidenceBucket" --format "value(name)" 2>$null
  if (-not $existing) {
    Run-Step "Create private evidence bucket" @(
      "gcloud", "storage", "buckets", "create", "gs://$EvidenceBucket",
      "--project", $ProjectId,
      "--location", $Region,
      "--uniform-bucket-level-access"
    )
  }
}

function Ensure-CloudBuildSourceBucket {
  $CloudBuildSourceBucket = "${ProjectId}_cloudbuild"
  $existing = & gcloud storage buckets describe "gs://$CloudBuildSourceBucket" --format "value(name)" 2>$null
  if (-not $existing) {
    Run-Step "Create Cloud Build source bucket" @(
      "gcloud", "storage", "buckets", "create", "gs://$CloudBuildSourceBucket",
      "--project", $ProjectId,
      "--location", "US",
      "--uniform-bucket-level-access"
    )
  }
}

function Get-CloudBuildServiceAccount {
  $email = (& gcloud builds get-default-service-account --project $ProjectId).Trim()
  if ($LASTEXITCODE -ne 0 -or -not $email) {
    throw "Failed to read Cloud Build default service account for $ProjectId"
  }
  return $email
}

function Ensure-CloudBuildPermissions {
  param([string]$BuildServiceAccount)
  $CloudBuildSourceBucket = "${ProjectId}_cloudbuild"
  Run-Step "Grant Cloud Build source read access" @(
    "gcloud", "storage", "buckets", "add-iam-policy-binding", "gs://$CloudBuildSourceBucket",
    "--member", "serviceAccount:$BuildServiceAccount",
    "--role", "roles/storage.objectViewer"
  )
  Run-Step "Grant Cloud Build Artifact Registry write access" @(
    "gcloud", "artifacts", "repositories", "add-iam-policy-binding", $Repository,
    "--project", $ProjectId,
    "--location", $Region,
    "--member", "serviceAccount:$BuildServiceAccount",
    "--role", "roles/artifactregistry.writer"
  )
  Run-Step "Grant Cloud Build log write access" @(
    "gcloud", "projects", "add-iam-policy-binding", $ProjectId,
    "--member", "serviceAccount:$BuildServiceAccount",
    "--role", "roles/logging.logWriter"
  )
}

function Deploy-Service {
  param(
    [string]$Name,
    [string]$Module,
    [bool]$Public,
    [string]$ExtraEnv = ""
  )
  $authFlag = if ($Public) { "--no-invoker-iam-check" } else { "--invoker-iam-check" }
  $envVars = @(
    "AKRETIC_SERVICE_MODULE=$Module",
    "AKRETIC_ENV=demo",
    "PROJECT_ID=$ProjectId",
    "REGION=$Region",
    "GOOGLE_CLOUD_PROJECT=$ProjectId",
    "GOOGLE_CLOUD_LOCATION=$Region",
    "VERTEX_MODEL=gemini-2.5-flash",
    "AKRETIC_GEMINI_MODE=vertex",
    "AKRETIC_CLOUD_RUN_AUTH=identity_token",
    "EVIDENCE_GCS_BUCKET=$EvidenceBucket",
    "EVIDENCE_GCS_PREFIX=p0-evidence"
  )
  if ($ExtraEnv) {
    $envVars += $ExtraEnv.Split(",", [System.StringSplitOptions]::RemoveEmptyEntries)
  }

  Run-Step "Deploy Cloud Run service $Name" @(
    "gcloud", "run", "deploy", $Name,
    "--project", $ProjectId,
    "--region", $Region,
    "--image", $Image,
    "--service-account", $RuntimeSaEmail,
    $authFlag,
    "--set-env-vars", ($envVars -join ",")
  )
}

function Get-ServiceUrl {
  param([string]$Name)
  $url = (& gcloud run services describe $Name --project $ProjectId --region $Region --format "value(status.url)")
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to read Cloud Run service URL for $Name"
  }
  return $url.Trim()
}

$RuntimeSaEmail = "$RuntimeServiceAccount@$ProjectId.iam.gserviceaccount.com"
$Image = "$Region-docker.pkg.dev/$ProjectId/$Repository/akretic-p0:$ImageTag"

$preflight = Test-DeploymentPreflight
if ($PreflightOnly) {
  $preflight | ConvertTo-Json -Depth 4
  return
}

Run-Step "Set active project" @("gcloud", "config", "set", "project", $ProjectId)

Run-Step "Enable required APIs" @(
  "gcloud", "services", "enable",
  "run.googleapis.com",
  "artifactregistry.googleapis.com",
  "cloudbuild.googleapis.com",
  "aiplatform.googleapis.com",
  "storage.googleapis.com",
  "logging.googleapis.com",
  "cloudtrace.googleapis.com",
  "secretmanager.googleapis.com",
  "--project", $ProjectId
)

Ensure-ServiceAccount -Email $RuntimeSaEmail
Ensure-ArtifactRepo
Ensure-Bucket
Ensure-CloudBuildSourceBucket
$BuildServiceAccount = Get-CloudBuildServiceAccount
Ensure-CloudBuildPermissions -BuildServiceAccount $BuildServiceAccount

Run-Step "Grant Vertex AI user to runtime service account" @(
  "gcloud", "projects", "add-iam-policy-binding", $ProjectId,
  "--member", "serviceAccount:$RuntimeSaEmail",
  "--role", "roles/aiplatform.user"
)

Run-Step "Grant bucket object admin to runtime service account" @(
  "gcloud", "storage", "buckets", "add-iam-policy-binding", "gs://$EvidenceBucket",
  "--member", "serviceAccount:$RuntimeSaEmail",
  "--role", "roles/storage.objectAdmin"
)

Run-Step "Build and push shared container image" @(
  "gcloud", "builds", "submit", ".",
  "--project", $ProjectId,
  "--config", "infra/cloudrun/cloudbuild.yaml",
  "--substitutions", "_IMAGE=$Image"
)

Deploy-Service -Name "akretic-policy-agent" -Module "services.gate0_lite.main:app" -Public $false
Deploy-Service -Name "akretic-knowledge-agent" -Module "services.rag_dmz_lite.main:app" -Public $false
Deploy-Service -Name "akretic-research-agent" -Module "agents.research_agent.main:app" -Public $false
Deploy-Service -Name "akretic-approval-evidence" -Module "agents.approval_evidence_agent.main:app" -Public $false

$PolicyUrl = Get-ServiceUrl "akretic-policy-agent"
$KnowledgeUrl = Get-ServiceUrl "akretic-knowledge-agent"
$ResearchUrl = Get-ServiceUrl "akretic-research-agent"
$ApprovalUrl = Get-ServiceUrl "akretic-approval-evidence"
$AgentEnv = "POLICY_AGENT_URL=$PolicyUrl,KNOWLEDGE_AGENT_URL=$KnowledgeUrl,RESEARCH_AGENT_URL=$ResearchUrl,APPROVAL_EVIDENCE_URL=$ApprovalUrl"

Deploy-Service -Name "akretic-root-orchestrator" -Module "agents.root_orchestrator.main:app" -Public $false -ExtraEnv $AgentEnv
$RootUrl = Get-ServiceUrl "akretic-root-orchestrator"

foreach ($service in @(
  "akretic-policy-agent",
  "akretic-knowledge-agent",
  "akretic-research-agent",
  "akretic-approval-evidence",
  "akretic-root-orchestrator"
)) {
  Run-Step "Grant runtime invoker on $service" @(
    "gcloud", "run", "services", "add-iam-policy-binding", $service,
    "--project", $ProjectId,
    "--region", $Region,
    "--member", "serviceAccount:$RuntimeSaEmail",
    "--role", "roles/run.invoker"
  )
}

Deploy-Service -Name "akretic-demo-ui" -Module "demo_ui.main:app" -Public $true -ExtraEnv "$AgentEnv,ROOT_ORCHESTRATOR_URL=$RootUrl"
$DemoUrl = Get-ServiceUrl "akretic-demo-ui"

Write-Host "`nDeployment complete."
Write-Host "Demo UI: $DemoUrl"
Write-Host "Root Orchestrator: $RootUrl"
Write-Host "Policy Agent: $PolicyUrl"
Write-Host "Knowledge Agent: $KnowledgeUrl"
Write-Host "Research Agent: $ResearchUrl"
Write-Host "Approval/Evidence Agent: $ApprovalUrl"
Write-Host "Evidence bucket: gs://$EvidenceBucket/p0-evidence/"
