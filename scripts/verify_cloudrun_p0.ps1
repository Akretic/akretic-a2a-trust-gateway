param(
  [string]$ProjectId = "akretic-a2a-trust-gateway",
  [string]$Region = "us-central1",
  [string]$DemoUrl = "https://akretic-demo-ui-oes3slkexq-uc.a.run.app",
  [string]$ApprovalEvidenceUrl = "https://akretic-approval-evidence-oes3slkexq-uc.a.run.app",
  [string]$Query = "VendorNova procurement security policy",
  [switch]$RequirePublic,
  [switch]$KeepReport
)

$ErrorActionPreference = "Stop"

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

function Assert-Match {
  param(
    [string]$Text,
    [string]$Pattern,
    [string]$Name
  )
  $match = [regex]::Match($Text, $Pattern)
  if (-not $match.Success -or -not $match.Groups[1].Value.Trim()) {
    throw "Unable to extract $Name from demo response"
  }
  return $match.Groups[1].Value.Trim()
}

function Assert-ContainsText {
  param(
    [string]$Text,
    [string]$Expected,
    [string]$Name
  )
  if (-not $Text.Contains($Expected)) {
    throw "$Name missing expected text: $Expected"
  }
}

$publicStatus = Get-HttpStatus "$DemoUrl/"
if ($RequirePublic -and $publicStatus -ne 200) {
  throw "Public demo URL returned HTTP $publicStatus"
}

$body = "persona=procurement_user&query=$([uri]::EscapeDataString($Query))"
$runResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$DemoUrl/run" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $body `
  -TimeoutSec 180

$runHtml = $runResponse.Content
if ($runHtml.Contains("LOCAL_DETERMINISTIC_SUMMARY_FOR_TESTS_ONLY") -or $runHtml.Contains("Mode: local")) {
  throw "Cloud Run demo unexpectedly used local Gemini mode"
}
if ($runHtml.Contains("Project Helios") -or $runHtml.Contains("confidential acquisition timing")) {
  throw "Denied document content appeared in the public demo response"
}
Assert-ContainsText $runHtml "Mode: vertex" "Gemini mode"
Assert-ContainsText $runHtml "Model: gemini-2.5-flash" "Gemini model"
Assert-ContainsText $runHtml "Project: $ProjectId" "Gemini project"
Assert-ContainsText $runHtml "Location: $Region" "Gemini location"
Assert-ContainsText $runHtml "ADK root wrapper proof." "ADK wrapper proof"
Assert-ContainsText $runHtml "akretic_root_vendor_review_workflow" "ADK workflow name"
Assert-ContainsText $runHtml "Denied before model context: executive_acquisition_memo." "denied source proof"
Assert-ContainsText $runHtml "approval_required: external/sensitive action is paused." "approval gate"
Assert-ContainsText $runHtml "Agent Card URL" "A2A Agent Card URL"
Assert-ContainsText $runHtml "Skill / intent" "A2A skill intent"
Assert-ContainsText $runHtml "Caller / callee" "A2A caller callee"
Assert-ContainsText $runHtml "Evidence event" "A2A evidence event"
$runId = Assert-Match $runHtml '<span>Run ID</span><strong>([^<]+)</strong>' "run_id"
$approvalId = Assert-Match $runHtml 'name="approval_id" value="([^"]+)"' "approval_id"

$decisionBody = "run_id=$([uri]::EscapeDataString($runId))&approval_id=$([uri]::EscapeDataString($approvalId))&reviewer_persona=security_reviewer&status=approved&reason=demo+reviewer+decision"
$decisionResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$DemoUrl/approval/decide" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $decisionBody `
  -TimeoutSec 180

$token = (& gcloud auth print-identity-token).Trim()
if (-not $token) {
  throw "Unable to mint gcloud identity token for private evidence report smoke"
}

$reportResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$($ApprovalEvidenceUrl.TrimEnd('/'))/evidence/$runId/report" `
  -Headers (@{ Authorization = "Bearer $token"; "x-akretic-persona" = "security_reviewer" }) `
  -TimeoutSec 60

$report = $reportResponse.Content | ConvertFrom-Json
if ($reportResponse.Content.Contains("Project Helios") -or $reportResponse.Content.Contains("confidential acquisition timing")) {
  throw "Denied document content appeared in the evidence report"
}
$latestModel = $report.summary.latest_model
if ($null -eq $latestModel) {
  throw "Evidence report is missing latest_model summary"
}
if ($latestModel.mode -ne "vertex") {
  throw "Evidence report model mode was '$($latestModel.mode)', expected 'vertex'"
}
if ($latestModel.model -ne "gemini-2.5-flash") {
  throw "Evidence report model was '$($latestModel.model)', expected 'gemini-2.5-flash'"
}
if ($latestModel.project_id -ne $ProjectId) {
  throw "Evidence report project was '$($latestModel.project_id)', expected '$ProjectId'"
}
if ($latestModel.location -ne $Region) {
  throw "Evidence report location was '$($latestModel.location)', expected '$Region'"
}
if ($latestModel.service_path -ne "Vertex AI Gemini via google-genai") {
  throw "Evidence report service_path was '$($latestModel.service_path)', expected Vertex AI Gemini path"
}
if ($latestModel.denied_source_ids -notcontains "executive_acquisition_memo") {
  throw "Evidence report did not include executive_acquisition_memo as a denied source ID"
}

$reportPath = $null
if ($KeepReport) {
  $outDir = Join-Path (Get-Location) "artifacts"
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null
  $reportPath = Join-Path $outDir "sample-evidence-report-$runId.json"
  Set-Content -Path $reportPath -Value $reportResponse.Content -Encoding UTF8
}

[ordered]@{
  project_id = $ProjectId
  region = $Region
  public_status = $publicStatus
  run_status = [int]$runResponse.StatusCode
  decision_status = [int]$decisionResponse.StatusCode
  report_status = [int]$reportResponse.StatusCode
  run_id = $runId
  approval_id = $approvalId
  report_path = $reportPath
  report_kept = [bool]$KeepReport
  has_denied_sources = $runHtml.Contains("Denied Sources")
  has_approval = $runHtml.Contains("Approval Request")
  has_verification = $runHtml.Contains("Evidence Verification")
  has_vertex_mode = $runHtml.Contains("Mode: vertex")
  has_vertex_model = $runHtml.Contains("Model: gemini-2.5-flash")
  has_vertex_project = $runHtml.Contains("Project: $ProjectId")
  has_vertex_location = $runHtml.Contains("Location: $Region")
  report_model_mode = $latestModel.mode
  report_model = $latestModel.model
  report_model_project = $latestModel.project_id
  report_model_location = $latestModel.location
  report_model_service_path = $latestModel.service_path
  report_valid = [bool]$report.verification.valid
} | ConvertTo-Json
