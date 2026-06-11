param(
  [string]$ProjectId = "akretic-a2a-trust-gateway",
  [string]$Region = "us-central1",
  [string]$Repository = "akretic",
  [string]$ImageTag = "",
  [ValidateSet("judging", "cost-saving")]
  [string]$DeployProfile = $(if ($env:AKRETIC_DEPLOY_PROFILE) { $env:AKRETIC_DEPLOY_PROFILE } else { "cost-saving" }),
  [string]$RuntimeServiceAccount = "akretic-p0-runtime",
  [string]$EvidenceBucket = "akretic-a2a-trust-gateway-evidence",
  [string]$CorpusBucket = "akretic-a2a-trust-gateway-corpus",
  [string]$CorpusPrefix = "p0-corpus",
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
$Gcloud = if ($IsWindows -or $env:OS -eq "Windows_NT") { "gcloud.cmd" } else { "gcloud" }
$Python = if ($IsWindows -or $env:OS -eq "Windows_NT") { ".\\.venv\\Scripts\\python.exe" } else { ".venv/bin/python" }
if (-not (Test-Path $Python)) {
  $Python = "python"
}
$MinInstances = if ($DeployProfile -eq "judging") { "1" } else { "0" }

function Run-Step {
  param(
    [string]$Description,
    [string[]]$Command
  )
  Write-Host "`n==> $Description"
  Write-Host ($Command -join " ")
  $exe = $Command[0]
  $args = $Command[1..($Command.Length - 1)]
  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    & $exe @args 2>&1 | ForEach-Object { Write-Host $_ }
    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorActionPreference
  }
  if ($exitCode -ne 0) {
    throw "Command failed with exit code ${exitCode}: $($Command -join ' ')"
  }
}

function Invoke-GcloudValue {
  param([string[]]$Arguments)
  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    $output = & $Gcloud @Arguments 2>$null
    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorActionPreference
  }
  if ($exitCode -ne 0) {
    return ""
  }
  return (($output | Out-String).Trim())
}

function Get-ServiceRevision {
  param([string]$Name)
  return Invoke-GcloudValue @("run", "services", "describe", $Name, "--project", $ProjectId, "--region", $Region, "--format", "value(status.latestReadyRevisionName)")
}

function Get-FileSha256 {
  param([string]$Text)
  $sha = [System.Security.Cryptography.SHA256]::Create()
  try {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
  } finally {
    $sha.Dispose()
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

  $activeAccount = Invoke-GcloudValue @("config", "get-value", "account")
  $activeProject = Invoke-GcloudValue @("config", "get-value", "project")
  Assert-Equal $activeAccount $ExpectedAccount "active gcloud account"
  Assert-Equal $activeProject $ProjectId "active gcloud project"

  $billingJson = Invoke-GcloudValue @("billing", "projects", "describe", $ProjectId, "--format=json")
  if (-not $billingJson) {
    throw "Failed to read billing state for $ProjectId"
  }
  $billing = $billingJson | ConvertFrom-Json
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
    corpus_bucket = $CorpusBucket
    corpus_prefix = $CorpusPrefix
  }
}

function Ensure-ServiceAccount {
  param([string]$Email)
  $existing = Invoke-GcloudValue @("iam", "service-accounts", "describe", $Email, "--project", $ProjectId, "--format", "value(email)")
  if (-not $existing) {
    Run-Step "Create runtime service account" @(
      $Gcloud, "iam", "service-accounts", "create", $RuntimeServiceAccount,
      "--project", $ProjectId,
      "--display-name", "Akretic P0 Cloud Run runtime"
    )
  }
}

function Ensure-ArtifactRepo {
  $existing = Invoke-GcloudValue @("artifacts", "repositories", "describe", $Repository, "--project", $ProjectId, "--location", $Region, "--format", "value(name)")
  if (-not $existing) {
    Run-Step "Create Artifact Registry repository" @(
      $Gcloud, "artifacts", "repositories", "create", $Repository,
      "--project", $ProjectId,
      "--repository-format", "docker",
      "--location", $Region,
      "--description", "Akretic A2A Trust Gateway P0 containers"
    )
  }
}

function Ensure-Bucket {
  $existing = Invoke-GcloudValue @("storage", "buckets", "describe", "gs://$EvidenceBucket", "--format", "value(name)")
  if (-not $existing) {
    Run-Step "Create private evidence bucket" @(
      $Gcloud, "storage", "buckets", "create", "gs://$EvidenceBucket",
      "--project", $ProjectId,
      "--location", $Region,
      "--uniform-bucket-level-access"
    )
  }
}

function Ensure-CorpusBucket {
  $existing = Invoke-GcloudValue @("storage", "buckets", "describe", "gs://$CorpusBucket", "--format", "value(name)")
  if (-not $existing) {
    Run-Step "Create private synthetic corpus bucket" @(
      $Gcloud, "storage", "buckets", "create", "gs://$CorpusBucket",
      "--project", $ProjectId,
      "--location", $Region,
      "--uniform-bucket-level-access"
    )
  }
}

function Upload-SyntheticCorpus {
  $prefix = $CorpusPrefix.Trim("/")
  $metadataTarget = if ($prefix) { "gs://$CorpusBucket/$prefix/metadata.json" } else { "gs://$CorpusBucket/metadata.json" }
  $documentsTarget = if ($prefix) { "gs://$CorpusBucket/$prefix/documents" } else { "gs://$CorpusBucket/documents" }
  Run-Step "Upload synthetic corpus metadata" @(
    $Gcloud, "storage", "cp", "corpus/metadata.json", $metadataTarget
  )
  Run-Step "Upload synthetic corpus documents" @(
    $Gcloud, "storage", "cp", "--recursive", "corpus/documents/*", $documentsTarget
  )
}

function Ensure-CloudBuildSourceBucket {
  $CloudBuildSourceBucket = "${ProjectId}_cloudbuild"
  $existing = Invoke-GcloudValue @("storage", "buckets", "describe", "gs://$CloudBuildSourceBucket", "--format", "value(name)")
  if (-not $existing) {
    Run-Step "Create Cloud Build source bucket" @(
      $Gcloud, "storage", "buckets", "create", "gs://$CloudBuildSourceBucket",
      "--project", $ProjectId,
      "--location", "US",
      "--uniform-bucket-level-access"
    )
  }
}

function Get-CloudBuildServiceAccount {
  $email = Invoke-GcloudValue @("builds", "get-default-service-account", "--project", $ProjectId)
  if (-not $email) {
    throw "Failed to read Cloud Build default service account for $ProjectId"
  }
  return $email
}

function Ensure-CloudBuildPermissions {
  param([string]$BuildServiceAccount)
  $CloudBuildSourceBucket = "${ProjectId}_cloudbuild"
  Run-Step "Grant Cloud Build source read access" @(
    $Gcloud, "storage", "buckets", "add-iam-policy-binding", "gs://$CloudBuildSourceBucket",
    "--member", "serviceAccount:$BuildServiceAccount",
    "--role", "roles/storage.objectViewer"
  )
  Run-Step "Grant Cloud Build Artifact Registry write access" @(
    $Gcloud, "artifacts", "repositories", "add-iam-policy-binding", $Repository,
    "--project", $ProjectId,
    "--location", $Region,
    "--member", "serviceAccount:$BuildServiceAccount",
    "--role", "roles/artifactregistry.writer"
  )
  Run-Step "Grant Cloud Build log write access" @(
    $Gcloud, "projects", "add-iam-policy-binding", $ProjectId,
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
    "AKRETIC_RUNTIME_MODE=cloud",
    "PROJECT_ID=$ProjectId",
    "REGION=$Region",
    "GOOGLE_CLOUD_PROJECT=$ProjectId",
    "GOOGLE_CLOUD_LOCATION=$Region",
    "VERTEX_MODEL=gemini-2.5-flash",
    "AKRETIC_GEMINI_MODE=vertex",
    "AKRETIC_CLOUD_RUN_AUTH=identity_token",
    "AKRETIC_A2A_CONNECT_TIMEOUT_SECONDS=5",
    "AKRETIC_A2A_READ_TIMEOUT_SECONDS=90",
    "AKRETIC_A2A_TOTAL_TIMEOUT_SECONDS=120",
    "AKRETIC_CORPUS_BACKEND=gcs",
    "AKRETIC_CORPUS_BUCKET=$CorpusBucket",
    "AKRETIC_CORPUS_PREFIX=$CorpusPrefix",
    "EVIDENCE_GCS_BUCKET=$EvidenceBucket",
    "EVIDENCE_GCS_PREFIX=p0-evidence",
    "AKRETIC_EVIDENCE_BUCKET=$EvidenceBucket",
    "AKRETIC_EVIDENCE_PREFIX=p0-evidence",
    "AKRETIC_RAG_MODE=lexical"
  )
  if ($ExtraEnv) {
    $envVars += $ExtraEnv.Split(",", [System.StringSplitOptions]::RemoveEmptyEntries)
  }

  Run-Step "Deploy Cloud Run service $Name" @(
    $Gcloud, "run", "deploy", $Name,
    "--project", $ProjectId,
    "--region", $Region,
    "--image", $DeployImage,
    "--service-account", $RuntimeSaEmail,
    $authFlag,
    "--min-instances", $MinInstances,
    "--set-env-vars", ($envVars -join ",")
  )
}

function Get-ServiceUrl {
  param([string]$Name)
  $url = Invoke-GcloudValue @("run", "services", "describe", $Name, "--project", $ProjectId, "--region", $Region, "--format", "value(status.url)")
  if (-not $url) {
    throw "Failed to read Cloud Run service URL for $Name"
  }
  return $url
}

$RuntimeSaEmail = "$RuntimeServiceAccount@$ProjectId.iam.gserviceaccount.com"
$CommitSha = (git rev-parse HEAD).Trim()
if (-not $ImageTag) {
  $ImageTag = $CommitSha
}
$ImageBase = "$Region-docker.pkg.dev/$ProjectId/$Repository/akretic-p0"
$Image = "${ImageBase}:$ImageTag"
$DeployImage = $Image

$PreviousRevisions = [ordered]@{}
foreach ($service in $AllowedServices) {
  $PreviousRevisions[$service] = Get-ServiceRevision $service
}

$preflight = Test-DeploymentPreflight
if ($PreflightOnly) {
  $preflight | ConvertTo-Json -Depth 4
  return
}

Run-Step "Set active project" @($Gcloud, "config", "set", "project", $ProjectId)

Run-Step "Enable required APIs" @(
  $Gcloud, "services", "enable",
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
Ensure-CorpusBucket
Ensure-CloudBuildSourceBucket
$BuildServiceAccount = Get-CloudBuildServiceAccount
Ensure-CloudBuildPermissions -BuildServiceAccount $BuildServiceAccount
Upload-SyntheticCorpus

Run-Step "Grant Vertex AI user to runtime service account" @(
  $Gcloud, "projects", "add-iam-policy-binding", $ProjectId,
  "--member", "serviceAccount:$RuntimeSaEmail",
  "--role", "roles/aiplatform.user"
)

Run-Step "Grant bucket object admin to runtime service account" @(
  $Gcloud, "storage", "buckets", "add-iam-policy-binding", "gs://$EvidenceBucket",
  "--member", "serviceAccount:$RuntimeSaEmail",
  "--role", "roles/storage.objectAdmin"
)

Run-Step "Grant synthetic corpus read access to runtime service account" @(
  $Gcloud, "storage", "buckets", "add-iam-policy-binding", "gs://$CorpusBucket",
  "--member", "serviceAccount:$RuntimeSaEmail",
  "--role", "roles/storage.objectViewer"
)

Run-Step "Build and push shared container image" @(
  $Gcloud, "builds", "submit", ".",
  "--project", $ProjectId,
  "--config", "infra/cloudrun/cloudbuild.yaml",
  "--substitutions", "_IMAGE=$Image"
)

$BuildId = Invoke-GcloudValue @("builds", "list", "--project", $ProjectId, "--sort-by", "~createTime", "--limit", "1", "--format", "value(id)")
$ImageDigest = Invoke-GcloudValue @("artifacts", "docker", "images", "describe", $Image, "--project", $ProjectId, "--format", "value(image_summary.digest)")
if (-not $ImageDigest) {
  throw "Failed to resolve immutable image digest for $Image"
}
$DeployImage = "${ImageBase}@${ImageDigest}"
Write-Host "Deploying immutable image $DeployImage"

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
    $Gcloud, "run", "services", "add-iam-policy-binding", $service,
    "--project", $ProjectId,
    "--region", $Region,
    "--member", "serviceAccount:$RuntimeSaEmail",
    "--role", "roles/run.invoker"
  )
}

Deploy-Service -Name "akretic-demo-ui" -Module "demo_ui.main:app" -Public $true -ExtraEnv "$AgentEnv,ROOT_ORCHESTRATOR_URL=$RootUrl"
$DemoUrl = Get-ServiceUrl "akretic-demo-ui"

$env:AKRETIC_CLOUD_RUN_AUTH = "identity_token"
$env:ROOT_ORCHESTRATOR_URL = $RootUrl
$env:POLICY_AGENT_URL = $PolicyUrl
$env:KNOWLEDGE_AGENT_URL = $KnowledgeUrl
$env:RESEARCH_AGENT_URL = $ResearchUrl
$env:APPROVAL_EVIDENCE_URL = $ApprovalUrl

Run-Step "Run P0 verifier gate" @(
  $Python, "scripts/p0_verify.py",
  "--base-url", $DemoUrl,
  "--mode", "cloud",
  "--root-url", $RootUrl,
  "--policy-url", $PolicyUrl,
  "--knowledge-url", $KnowledgeUrl,
  "--research-url", $ResearchUrl,
  "--approval-url", $ApprovalUrl,
  "--expect-vertex",
  "--fail-on-local",
  "--expect-corpus-backend", "gcs",
  "--expect-freeform-playground",
  "--expect-corpus-explorer",
  "--expect-corpus-live-retrieval",
  "--expect-decision-receipts",
  "--expect-trust-receipt",
  "--expect-model-context-envelope",
  "--expect-red-team-cards"
)

Run-Step "Run five-run readiness burn-in" @(
  $Python, "scripts/readiness_burnin.py",
  "--base-url", $DemoUrl,
  "--runs", "5",
  "--expect-zero-5xx",
  "--expect-vertex",
  "--fail-on-local",
  "--root-url", $RootUrl,
  "--policy-url", $PolicyUrl,
  "--knowledge-url", $KnowledgeUrl,
  "--research-url", $ResearchUrl,
  "--approval-url", $ApprovalUrl
)

$CurrentRevisions = [ordered]@{
  "akretic-demo-ui" = Get-ServiceRevision "akretic-demo-ui"
  "akretic-root-orchestrator" = Get-ServiceRevision "akretic-root-orchestrator"
  "akretic-policy-agent" = Get-ServiceRevision "akretic-policy-agent"
  "akretic-knowledge-agent" = Get-ServiceRevision "akretic-knowledge-agent"
  "akretic-research-agent" = Get-ServiceRevision "akretic-research-agent"
  "akretic-approval-evidence" = Get-ServiceRevision "akretic-approval-evidence"
}
$ServiceUrls = [ordered]@{
  "akretic-demo-ui" = $DemoUrl
  "akretic-root-orchestrator" = $RootUrl
  "akretic-policy-agent" = $PolicyUrl
  "akretic-knowledge-agent" = $KnowledgeUrl
  "akretic-research-agent" = $ResearchUrl
  "akretic-approval-evidence" = $ApprovalUrl
}
$MinInstanceSettings = [ordered]@{}
foreach ($service in $AllowedServices) {
  $MinInstanceSettings[$service] = [int]$MinInstances
}
$RollbackCommands = @()
foreach ($service in $AllowedServices) {
  $previous = $PreviousRevisions[$service]
  if ($previous) {
    $RollbackCommands += "gcloud run services update-traffic $service --project $ProjectId --region $Region --to-revisions $previous=100"
  }
}
$BurnIn = Get-Content "readiness-burnin-output.json" -Raw | ConvertFrom-Json
$EnvironmentMaterial = (@{
  project_id = $ProjectId
  region = $Region
  deploy_profile = $DeployProfile
  min_instances = $MinInstanceSettings
  corpus_bucket = $CorpusBucket
  corpus_prefix = $CorpusPrefix
  evidence_bucket = $EvidenceBucket
  vertex_model = "gemini-2.5-flash"
} | ConvertTo-Json -Depth 6)
$DeployManifest = [ordered]@{
  packet_type = "cloud_judge_deploy_manifest"
  created_at = (Get-Date).ToUniversalTime().ToString("o")
  deploy_profile = $DeployProfile
  build_id = $BuildId
  commit_sha = $CommitSha
  image_digest = $ImageDigest
  deployed_image = $DeployImage
  service_revisions = $CurrentRevisions
  previous_revisions = $PreviousRevisions
  service_urls = $ServiceUrls
  min_instances = $MinInstanceSettings
  environment_hash = Get-FileSha256 $EnvironmentMaterial
  corpus_backend = "gcs"
  model_metadata = @{
    runtime_mode = "cloud"
    model_mode = "vertex"
    model = "gemini-2.5-flash"
    project_id = $ProjectId
    location = $Region
  }
  p0_verifier_run_id = (($BurnIn.runs | Select-Object -First 1).run_id)
  readiness_burn_in_result = $BurnIn.ok
  packet_filename = $null
  rollback_commands = $RollbackCommands
}
$DeployManifest | ConvertTo-Json -Depth 10 | Set-Content -Path "deploy-manifest.json" -Encoding UTF8

Run-Step "Generate final cloud handoff packet" @(
  $Python, "scripts/make_final_handoff.py",
  "--base-url", $DemoUrl,
  "--mode", "cloud",
  "--root-url", $RootUrl,
  "--policy-url", $PolicyUrl,
  "--knowledge-url", $KnowledgeUrl,
  "--research-url", $ResearchUrl,
  "--approval-url", $ApprovalUrl,
  "--project-label", $ProjectId,
  "--deploy-manifest", "deploy-manifest.json"
)

Write-Host "`nDeployment complete."
Write-Host "Demo UI: $DemoUrl"
Write-Host "Root Orchestrator: $RootUrl"
Write-Host "Policy Agent: $PolicyUrl"
Write-Host "Knowledge Agent: $KnowledgeUrl"
Write-Host "Research Agent: $ResearchUrl"
Write-Host "Approval/Evidence Agent: $ApprovalUrl"
Write-Host "Evidence bucket: gs://$EvidenceBucket/p0-evidence/"
Write-Host "Synthetic corpus: gs://$CorpusBucket/$CorpusPrefix/"
