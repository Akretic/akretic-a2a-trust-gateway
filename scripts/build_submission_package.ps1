param(
  [string]$ZipPath = "dist/akretic-a2a-trust-gateway-submission.zip",
  [string]$PublicBriefPdf = "dist/akretic-a2a-trust-gateway-public-brief.pdf",
  [string]$VideoUrlFile = "dist/video_url.txt",
  [int]$MaxSizeMb = 35
)

$ErrorActionPreference = "Stop"

function Copy-RequiredFile {
  param(
    [string]$Source,
    [string]$Destination
  )
  if (-not (Test-Path -LiteralPath $Source)) {
    throw "Required package file missing: $Source"
  }
  $targetDir = Split-Path -Parent $Destination
  if ($targetDir) {
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
  }
  Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

New-Item -ItemType Directory -Force -Path "dist" | Out-Null
if (-not (Test-Path -LiteralPath $VideoUrlFile)) {
  Set-Content -LiteralPath $VideoUrlFile -Value "CLIENT_INPUT_REQUIRED - replace with hosted 1-2 minute demo video URL after upload." -Encoding UTF8
}

$stage = Join-Path ".akretic" "p5-submission-package"
$resolvedWorkspace = (Resolve-Path ".").Path
if (Test-Path -LiteralPath $stage) {
  $resolvedStage = (Resolve-Path $stage).Path
  if (-not $resolvedStage.StartsWith($resolvedWorkspace, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to remove stage path outside workspace: $resolvedStage"
  }
  Remove-Item -LiteralPath $resolvedStage -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$docs = @(
  "docs/p5_acceptance.md",
  "docs/devpost_answers.md",
  "docs/demo_video_script.md",
  "docs/video_shot_list.md",
  "docs/public_brief.md",
  "docs/submission_checklist.md",
  "docs/submission_package.md",
  "docs/challenge_readiness_remediation.md",
  "docs/judge_readiness.md",
  "docs/architecture.md",
  "docs/architecture.mmd",
  "docs/deployment.md",
  "docs/deployment_notes.md"
)

foreach ($doc in $docs) {
  Copy-RequiredFile $doc (Join-Path $stage $doc)
}

Copy-RequiredFile "README.md" (Join-Path $stage "README.md")
Copy-RequiredFile $PublicBriefPdf (Join-Path $stage $PublicBriefPdf)
Copy-RequiredFile $VideoUrlFile (Join-Path $stage $VideoUrlFile)
Copy-RequiredFile "output/architecture/akretic-a2a-architecture.png" (Join-Path $stage "artifacts/architecture/akretic-a2a-architecture.png")
Copy-RequiredFile "output/architecture/akretic-a2a-architecture.svg" (Join-Path $stage "artifacts/architecture/akretic-a2a-architecture.svg")

$latestEvidence = Get-ChildItem -Path "artifacts" -Filter "sample-evidence-report-*.json" -File |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
if (-not $latestEvidence) {
  throw "No sample evidence report found under artifacts/"
}
Copy-RequiredFile $latestEvidence.FullName (Join-Path $stage ("artifacts/" + $latestEvidence.Name))

$screenshots = @(
  "artifacts/screenshots/demo-home.png",
  "artifacts/screenshots/demo-review-result.png",
  "artifacts/screenshots/evidence-report.png"
)
foreach ($screenshot in $screenshots) {
  Copy-RequiredFile $screenshot (Join-Path $stage $screenshot)
}

if (Test-Path -LiteralPath $ZipPath) {
  Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $ZipPath -Force

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path $ZipPath).Path)
try {
  $blocked = $zip.Entries | Where-Object {
    $_.FullName -match '\.(mp4|mov|webm|mkv|avi|prproj|fcpxml)$'
  }
  if ($blocked) {
    throw "Package contains blocked video/editing artifact: $($blocked[0].FullName)"
  }
}
finally {
  $zip.Dispose()
}

$sizeBytes = (Get-Item -LiteralPath $ZipPath).Length
$sizeMb = [math]::Round($sizeBytes / 1MB, 2)
if ($sizeMb -gt $MaxSizeMb) {
  throw "Package is $sizeMb MB, above $MaxSizeMb MB limit"
}

[ordered]@{
  zip_path = $ZipPath
  size_mb = $sizeMb
  evidence_report = $latestEvidence.Name
  video_url_file = $VideoUrlFile
  video_binaries_included = $false
} | ConvertTo-Json
