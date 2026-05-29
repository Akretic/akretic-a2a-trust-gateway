param(
  [string]$DemoUrl = "https://akretic-demo-ui-oes3slkexq-uc.a.run.app",
  [string]$ProjectId = "akretic-a2a-trust-gateway",
  [string]$Region = "us-central1",
  [string]$Query = "VendorNova procurement security policy"
)

$ErrorActionPreference = "Stop"

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

function Assert-NotContainsText {
  param(
    [string]$Text,
    [string]$Unexpected,
    [string]$Name
  )
  if ($Text.Contains($Unexpected)) {
    throw "$Name contained denied-content canary text"
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

$baseUrl = $DemoUrl.TrimEnd("/")
$homeResponse = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/" -TimeoutSec 60
$homeHtml = $homeResponse.Content

Assert-ContainsText $homeHtml "Akretic A2A Trust Gateway" "home brand"
Assert-ContainsText $homeHtml "Agents collaborate. Gemini does not authorize." "home thesis"
Assert-ContainsText $homeHtml "controlled VendorNova review" "home buyer workflow"
Assert-ContainsText $homeHtml "Challenge prototype" "home prototype label"
Assert-ContainsText $homeHtml "Synthetic data" "home synthetic-data label"
Assert-ContainsText $homeHtml "Cloud Run + Vertex Gemini" "home Vertex Cloud Run chip"
Assert-ContainsText $homeHtml "A2A protocol proof" "home A2A proof chip"
Assert-ContainsText $homeHtml "What this demo proves" "home proof narrative"
Assert-ContainsText $homeHtml "Run the controlled VendorNova review." "home scenario form"
Assert-ContainsText $homeHtml "Start VendorNova Review" "home start button"

$body = "persona=procurement_user&query=$([uri]::EscapeDataString($Query))"
$runResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$baseUrl/run" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $body `
  -TimeoutSec 180

$runHtml = $runResponse.Content
Assert-ContainsText $runHtml "VendorNova Review" "review page"
Assert-ContainsText $runHtml "Proof Path From This Run" "review proof storyboard"
Assert-ContainsText $runHtml "The result mirrors the homepage story with the actual run evidence." "review proof narrative"
Assert-ContainsText $runHtml "<span>Run ID</span>" "run ID metric"
Assert-ContainsText $runHtml "Mode: vertex" "Vertex mode"
Assert-ContainsText $runHtml "Model: gemini-2.5-flash" "Gemini model"
Assert-ContainsText $runHtml "Project: $ProjectId" "Gemini project"
Assert-ContainsText $runHtml "Location: $Region" "Gemini location"
Assert-ContainsText $runHtml "Gate0-lite remains the policy decision point" "policy boundary"
Assert-ContainsText $runHtml "Denied before model context: executive_acquisition_memo." "denied-source proof"
Assert-ContainsText $runHtml "denied source text is not provided to Gemini" "denied-text boundary"
Assert-ContainsText $runHtml "approval_required: external/sensitive action is paused." "approval gate"
Assert-ContainsText $runHtml "Approval Request" "approval request"
Assert-ContainsText $runHtml "Record reviewer decision" "reviewer decision path"
Assert-ContainsText $runHtml "A2A Proof" "A2A proof"
Assert-ContainsText $runHtml "Agent Card resolved" "Agent Card proof"
Assert-ContainsText $runHtml "correlation_id" "A2A correlation ID"
Assert-ContainsText $runHtml "Evidence proof: valid hash chain." "evidence proof"
Assert-ContainsText $runHtml "Open sample evidence report" "sample evidence link"
Assert-NotContainsText $runHtml "LOCAL_DETERMINISTIC_SUMMARY_FOR_TESTS_ONLY" "review page"
Assert-NotContainsText $runHtml "Project Helios" "review page"
Assert-NotContainsText $runHtml "confidential acquisition timing" "review page"

$runId = Assert-Match $runHtml '<span>Run ID</span><strong>([^<]+)</strong>' "run_id"
$approvalId = Assert-Match $runHtml 'name="approval_id" value="([^"]+)"' "approval_id"

$decisionBody = "run_id=$([uri]::EscapeDataString($runId))&approval_id=$([uri]::EscapeDataString($approvalId))&reviewer_persona=security_reviewer&status=approved&reason=judge+readiness+check"
$decisionResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$baseUrl/approval/decide" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $decisionBody `
  -TimeoutSec 180

$decisionHtml = $decisionResponse.Content
Assert-ContainsText $decisionHtml "Approval Decision" "approval decision page"
Assert-ContainsText $decisionHtml "Reviewer approve/reject path is visible." "reviewer decision proof"
Assert-ContainsText $decisionHtml "Evidence proof: valid hash chain." "approval evidence proof"
Assert-NotContainsText $decisionHtml "Project Helios" "approval page"
Assert-NotContainsText $decisionHtml "confidential acquisition timing" "approval page"

$sampleResponse = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/sample-evidence-report" -TimeoutSec 60
$sampleText = $sampleResponse.Content
Assert-NotContainsText $sampleText "Project Helios" "sample evidence report"
Assert-NotContainsText $sampleText "confidential acquisition timing" "sample evidence report"
$sampleReport = $sampleText | ConvertFrom-Json
if (-not [bool]$sampleReport.verification.valid) {
  throw "Sample evidence report verification is not valid"
}
if ($sampleReport.summary.latest_model.mode -ne "vertex") {
  throw "Sample evidence report model mode was '$($sampleReport.summary.latest_model.mode)', expected 'vertex'"
}
if ($sampleReport.summary.latest_model.denied_source_ids -notcontains "executive_acquisition_memo") {
  throw "Sample evidence report does not include executive_acquisition_memo as a denied source ID"
}

[ordered]@{
  demo_url = "$baseUrl/"
  public_status = [int]$homeResponse.StatusCode
  run_status = [int]$runResponse.StatusCode
  decision_status = [int]$decisionResponse.StatusCode
  sample_report_status = [int]$sampleResponse.StatusCode
  run_id = $runId
  approval_id = $approvalId
  vertex_mode_visible = $runHtml.Contains("Mode: vertex")
  denied_source_id_visible = $runHtml.Contains("Denied before model context: executive_acquisition_memo.")
  approval_gate_visible = $runHtml.Contains("approval_required: external/sensitive action is paused.")
  a2a_proof_visible = $runHtml.Contains("A2A Proof") -and $runHtml.Contains("correlation_id")
  evidence_verify_visible = $runHtml.Contains("Evidence proof: valid hash chain.")
  sample_report_valid = [bool]$sampleReport.verification.valid
} | ConvertTo-Json
