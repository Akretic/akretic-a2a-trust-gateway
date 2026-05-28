param(
  [string]$ProjectId = "akretic-a2a-trust-gateway",
  [string]$Region = "us-central1",
  [string]$DemoUrl = "https://akretic-demo-ui-oes3slkexq-uc.a.run.app",
  [string]$ApprovalEvidenceUrl = "https://akretic-approval-evidence-oes3slkexq-uc.a.run.app",
  [string]$Query = "VendorNova procurement security policy",
  [switch]$RequirePublic
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

$publicStatus = Get-HttpStatus "$DemoUrl/"
if ($RequirePublic -and $publicStatus -ne 200) {
  throw "Public demo URL returned HTTP $publicStatus"
}

$token = (& gcloud auth print-identity-token).Trim()
if (-not $token) {
  throw "Unable to mint gcloud identity token for authenticated Cloud Run smoke"
}
$headers = @{ Authorization = "Bearer $token" }

$body = "persona=procurement_user&query=$([uri]::EscapeDataString($Query))"
$runResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$DemoUrl/run" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $body `
  -TimeoutSec 180

$runHtml = $runResponse.Content
$runId = Assert-Match $runHtml '<span>Run ID</span><strong>([^<]+)</strong>' "run_id"
$approvalId = Assert-Match $runHtml 'name="approval_id" value="([^"]+)"' "approval_id"

$decisionBody = "run_id=$([uri]::EscapeDataString($runId))&approval_id=$([uri]::EscapeDataString($approvalId))&reviewer_persona=security_reviewer&status=approved&reason=demo+reviewer+decision"
$decisionResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$DemoUrl/approval/decide" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $decisionBody `
  -TimeoutSec 180

$reportResponse = Invoke-WebRequest `
  -UseBasicParsing `
  -Uri "$($ApprovalEvidenceUrl.TrimEnd('/'))/evidence/$runId/report" `
  -Headers (@{ Authorization = "Bearer $token"; "x-akretic-persona" = "security_reviewer" }) `
  -TimeoutSec 60

$outDir = Join-Path (Get-Location) "artifacts"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$reportPath = Join-Path $outDir "sample-evidence-report-$runId.json"
Set-Content -Path $reportPath -Value $reportResponse.Content -Encoding UTF8

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
  has_denied_sources = $runHtml.Contains("Denied Sources")
  has_approval = $runHtml.Contains("Approval Request")
  has_verification = $runHtml.Contains("Evidence Verification")
  report_valid = $reportResponse.Content.Contains('"valid":true')
} | ConvertTo-Json
