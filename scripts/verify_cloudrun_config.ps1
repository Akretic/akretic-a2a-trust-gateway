param(
  [string]$ProjectId = "akretic-a2a-trust-gateway",
  [string]$Region = "us-central1",
  [string]$ExpectedAccount = "sean.w@akretic.com",
  [string]$RuntimeServiceAccount = "akretic-p0-runtime",
  [string]$EvidenceBucket = "akretic-a2a-trust-gateway-evidence",
  [switch]$SkipHttpExposureChecks
)

$ErrorActionPreference = "Stop"

$services = @(
  @{
    key = "demo_ui"
    name = "akretic-demo-ui"
    module = "demo_ui.main:app"
    public = $true
    required_extra_env = @("ROOT_ORCHESTRATOR_URL", "POLICY_AGENT_URL", "KNOWLEDGE_AGENT_URL", "RESEARCH_AGENT_URL", "APPROVAL_EVIDENCE_URL")
  },
  @{
    key = "root_orchestrator"
    name = "akretic-root-orchestrator"
    module = "agents.root_orchestrator.main:app"
    public = $false
    required_extra_env = @("POLICY_AGENT_URL", "KNOWLEDGE_AGENT_URL", "RESEARCH_AGENT_URL", "APPROVAL_EVIDENCE_URL")
  },
  @{
    key = "policy_agent"
    name = "akretic-policy-agent"
    module = "services.gate0_lite.main:app"
    public = $false
    required_extra_env = @()
  },
  @{
    key = "knowledge_agent"
    name = "akretic-knowledge-agent"
    module = "services.rag_dmz_lite.main:app"
    public = $false
    required_extra_env = @()
  },
  @{
    key = "research_agent"
    name = "akretic-research-agent"
    module = "agents.research_agent.main:app"
    public = $false
    required_extra_env = @()
  },
  @{
    key = "approval_evidence_agent"
    name = "akretic-approval-evidence"
    module = "agents.approval_evidence_agent.main:app"
    public = $false
    required_extra_env = @()
  }
)

function Get-HttpStatus {
  param([string]$Url)
  try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 30
    return [int]$response.StatusCode
  } catch {
    if ($_.Exception.Response) {
      return [int]$_.Exception.Response.StatusCode
    }
    throw
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

function Get-EnvMap {
  param([object]$Service)
  $map = @{}
  foreach ($item in @($Service.spec.template.spec.containers[0].env)) {
    $map[$item.name] = $item.value
  }
  return $map
}

function Assert-NoPublicInvoker {
  param(
    [object]$Policy,
    [string]$ServiceName
  )
  foreach ($binding in @($Policy.bindings)) {
    foreach ($member in @($binding.members)) {
      if ($member -in @("allUsers", "allAuthenticatedUsers")) {
        throw "$ServiceName IAM policy contains public member '$member'"
      }
    }
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

$runtimeSaEmail = "$RuntimeServiceAccount@$ProjectId.iam.gserviceaccount.com"
$results = @()
$serviceUrls = @{}

foreach ($expected in $services) {
  $service = gcloud run services describe $expected.name --project $ProjectId --region $Region --format=json | ConvertFrom-Json
  $policy = gcloud run services get-iam-policy $expected.name --project $ProjectId --region $Region --format=json | ConvertFrom-Json
  Assert-NoPublicInvoker -Policy $policy -ServiceName $expected.name

  $ready = @($service.status.conditions | Where-Object { $_.type -eq "Ready" })[0]
  Assert-Equal $ready.status "True" "$($expected.name) Ready condition"
  Assert-Equal $service.status.latestReadyRevisionName $service.status.latestCreatedRevisionName "$($expected.name) latest ready revision"
  Assert-Equal $service.spec.template.spec.serviceAccountName $runtimeSaEmail "$($expected.name) runtime service account"

  $traffic = @($service.status.traffic)[0]
  Assert-Equal $traffic.percent 100 "$($expected.name) traffic percent"
  Assert-Equal $traffic.revisionName $service.status.latestReadyRevisionName "$($expected.name) serving revision"

  $env = Get-EnvMap -Service $service
  Assert-Equal $env["AKRETIC_SERVICE_MODULE"] $expected.module "$($expected.name) service module"
  Assert-Equal $env["AKRETIC_ENV"] "demo" "$($expected.name) environment"
  Assert-Equal $env["PROJECT_ID"] $ProjectId "$($expected.name) PROJECT_ID"
  Assert-Equal $env["REGION"] $Region "$($expected.name) REGION"
  Assert-Equal $env["GOOGLE_CLOUD_PROJECT"] $ProjectId "$($expected.name) GOOGLE_CLOUD_PROJECT"
  Assert-Equal $env["GOOGLE_CLOUD_LOCATION"] $Region "$($expected.name) GOOGLE_CLOUD_LOCATION"
  Assert-Equal $env["VERTEX_MODEL"] "gemini-2.5-flash" "$($expected.name) VERTEX_MODEL"
  Assert-Equal $env["AKRETIC_GEMINI_MODE"] "vertex" "$($expected.name) AKRETIC_GEMINI_MODE"
  Assert-Equal $env["AKRETIC_CLOUD_RUN_AUTH"] "identity_token" "$($expected.name) AKRETIC_CLOUD_RUN_AUTH"
  Assert-Equal $env["EVIDENCE_GCS_BUCKET"] $EvidenceBucket "$($expected.name) EVIDENCE_GCS_BUCKET"
  Assert-Equal $env["EVIDENCE_GCS_PREFIX"] "p0-evidence" "$($expected.name) EVIDENCE_GCS_PREFIX"
  foreach ($requiredEnv in $expected.required_extra_env) {
    if (-not $env.ContainsKey($requiredEnv) -or -not $env[$requiredEnv]) {
      throw "$($expected.name) missing required env var $requiredEnv"
    }
  }

  $publicAnnotation = $service.metadata.annotations.'run.googleapis.com/invoker-iam-disabled'
  if ($expected.public) {
    Assert-Equal $publicAnnotation "true" "$($expected.name) public invoker IAM disabled annotation"
  } elseif ($publicAnnotation -eq "true") {
    throw "$($expected.name) unexpectedly disables the Cloud Run invoker IAM check"
  }

  $members = @()
  foreach ($binding in @($policy.bindings | Where-Object { $_.role -eq "roles/run.invoker" })) {
    $members += @($binding.members)
  }
  if (-not $expected.public -and $members -notcontains "serviceAccount:$runtimeSaEmail") {
    throw "$($expected.name) is missing roles/run.invoker for $runtimeSaEmail"
  }

  $status = $null
  if (-not $SkipHttpExposureChecks) {
    $urlToCheck = if ($expected.public) { "$($service.status.url)/" } else { "$($service.status.url)/healthz" }
    $status = Get-HttpStatus $urlToCheck
    if ($expected.public -and $status -ne 200) {
      throw "$($expected.name) public URL returned HTTP $status"
    }
    if (-not $expected.public -and $status -notin @(401, 403, 404)) {
      throw "$($expected.name) private URL returned HTTP $status to unauthenticated request"
    }
  }

  $serviceUrls[$expected.name] = $service.status.url
  $results += [ordered]@{
    service = $expected.name
    public = [bool]$expected.public
    url = $service.status.url
    latest_ready_revision = $service.status.latestReadyRevisionName
    serving_revision = $traffic.revisionName
    unauthenticated_status = $status
  }
}

[ordered]@{
  project_id = $ProjectId
  region = $Region
  active_account = $activeAccount
  active_project = $activeProject
  billing_enabled = [bool]$billing.billingEnabled
  runtime_service_account = $runtimeSaEmail
  services_checked = $results
} | ConvertTo-Json -Depth 6
