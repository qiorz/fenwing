param([switch]$SkipSmoke)
$ErrorActionPreference = 'Stop'
$scripts = 'D:\ff-ohos\scripts'
$fail = 0

function Step([string]$name, [scriptblock]$block) {
  Write-Host "=== $name ===" -ForegroundColor Cyan
  & $block
  if ($LASTEXITCODE -ne 0) {
    Write-Host "STEP FAILED: $name" -ForegroundColor Red
    $script:fail++
  }
}

Step 'build' { & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $scripts 'build-all.ps1') }
Step 'verify' { & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $scripts 'verify-snapshot.ps1') }
if (-not $SkipSmoke) {
  Step 'smoke' { & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $scripts 'smoke-test.ps1') }
}

if ($fail -eq 0) { Write-Host 'CI LOCAL: PASS' -ForegroundColor Green; exit 0 }
Write-Host ("CI LOCAL: {0} STEP(S) FAILED" -f $fail) -ForegroundColor Red
exit 1
