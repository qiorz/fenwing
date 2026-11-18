param(
  [switch]$SkipHsp,
  [switch]$SkipHap
)
$ErrorActionPreference = 'Stop'
$ever = 'C:\Program Files\Huawei\DevEco Studio'
$proj = 'D:\ff-ohos\work\firefoxport'
$env:PATH = "$ever\tools\node;$ever\tools\ohpm\bin;$env:PATH"
$env:NODE_HOME = "$ever\tools\node"
$env:DEVECO_SDK_HOME = "$ever\sdk"

Push-Location $proj
try {
  $targets = @()
  if (-not $SkipHsp) { $targets += 'assembleHsp' }
  if (-not $SkipHap) { $targets += 'assembleHap' }
  if ($targets.Count -eq 0) { throw 'nothing to build' }
  & "$ever\tools\hvigor\bin\hvigorw.bat" @targets --no-daemon 2>&1 | Tee-Object 'D:\ff-ohos\logs\build-all.log' | Out-Null
  $code = $LASTEXITCODE
} finally {
  Pop-Location
}

if ($code -ne 0) {
  Write-Host "BUILD FAILED (exit $code). See D:\ff-ohos\logs\build-all.log" -ForegroundColor Red
  Select-String -Path 'D:\ff-ohos\logs\build-all.log' -Pattern 'Error Message' -Context 0,2 |
    Select-Object -First 5 | ForEach-Object { $_.Line.Trim() }
  exit $code
}

$hsp = Join-Path $proj 'gecko\build\default\outputs\default\gecko-default-signed.hsp'
$hap = Join-Path $proj 'entry\build\default\outputs\default\entry-default-signed.hap'
foreach ($f in @($hsp, $hap)) {
  if (Test-Path $f) {
    $mb = [math]::Round((Get-Item $f).Length / 1MB, 1)
    Write-Host ("OK  {0}  {1} MB" -f (Split-Path $f -Leaf), $mb) -ForegroundColor Green
  }
}
exit 0
