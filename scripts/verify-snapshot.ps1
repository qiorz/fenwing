param(
  [string]$Project = 'D:\ff-ohos\work\firefoxport',
  [int]$MaxHspMb = 270
)
$ErrorActionPreference = 'Continue'
$fail = 0
function Check([string]$name, [bool]$ok, [string]$detail = '') {
  if ($ok) { Write-Host ("PASS  {0} {1}" -f $name, $detail) -ForegroundColor Green }
  else { Write-Host ("FAIL  {0} {1}" -f $name, $detail) -ForegroundColor Red; $script:fail++ }
}

$hsp = Join-Path $Project 'gecko\build\default\outputs\default\gecko-default-signed.hsp'
$hap = Join-Path $Project 'entry\build\default\outputs\default\entry-default-signed.hap'
$libxul = Join-Path $Project 'gecko\libs\arm64-v8a\libxul.so'
$omni = Join-Path $Project 'gecko\src\main\resources\rawfile\omni.ja'
$moduleJson = Join-Path $Project 'entry\src\main\module.json5'

Check 'artifacts exist' ((Test-Path $hsp) -and (Test-Path $hap))
if (Test-Path $hsp) {
  $mb = (Get-Item $hsp).Length / 1MB
  Check 'HSP size budget' ($mb -le $MaxHspMb) ("{0:N1} MB <= {1} MB" -f $mb, $MaxHspMb)
}

# .permission section present (JIT ACL)
$readelf = & wsl.exe -d Ubuntu-24.04 -u dev -- readelf -S /mnt/d/ff-ohos/work/firefoxport/gecko/libs/arm64-v8a/libxul.so 2>&1
Check 'libxul .permission section' (($readelf -join "`n") -match '\.permission')

# omni markers
$omniOut = & wsl.exe -d Ubuntu-24.04 -u dev -- unzip -p /mnt/d/ff-ohos/work/firefoxport/gecko/src/main/resources/rawfile/omni.ja chrome/geckoview/content/geckoview.js 2>&1
$omniText = $omniOut -join "`n"
Check 'omni geckoview.js context menu' (($omniText -match 'ohosOpenContextMenu') -and ($omniText -match '__opentab__'))
Check 'omni deflate (<=30MB)' (((Get-Item $omni).Length / 1MB) -le 30) ("{0:N1} MB" -f ((Get-Item $omni).Length / 1MB))

# ACL declarations
$mj = Get-Content $moduleJson -Raw
Check 'ACL: writable code memory' ($mj -match 'ALLOW_WRITABLE_CODE_MEMORY')
Check 'ACL: disable code memory protection' ($mj -match 'DISABLE_CODE_MEMORY_PROTECTION')

# no CRLF in critical ArkTS sources
$bad = @()
foreach ($f in @('entry\src\main\ets\pages\BrowserPage.ets', 'entry\src\main\ets\components\AddressBar.ets',
                 'gecko\src\main\ets\GeckoViewBoot.ets')) {
  $p = Join-Path $Project $f
  if (Test-Path $p) {
    $bytes = [System.IO.File]::ReadAllBytes($p)
    if ([Array]::IndexOf($bytes, [byte]13) -ge 0) { $bad += $f }
  }
}
Check 'no CRLF in ArkTS sources' ($bad.Count -eq 0) ($bad -join ', ')

# P4 compliance: license package + branding
$legal = Join-Path $Project 'entry\src\main\resources\rawfile\legal'
Check 'legal files packaged' ((Test-Path (Join-Path $legal 'LICENSE-MPL-2.0.txt')) -and
                             (Test-Path (Join-Path $legal 'THIRD-PARTY-NOTICES.txt')) -and
                             (Test-Path (Join-Path $legal 'SOURCE-OFFER.txt')))
$appStr = Get-Content (Join-Path $Project 'AppScope\resources\base\element\string.json') -Raw
Check 'app name not Firefox-branded' ($appStr -notmatch 'firefox')
$indexPath = Join-Path $Project 'entry\src\main\ets\pages\Index.ets'
if (Test-Path $indexPath) {
  $indexText = Get-Content $indexPath -Raw
  Check 'no Firefox branding in Index.ets' ($indexText -notmatch 'Firefox')
}

Write-Host ''
if ($fail -eq 0) { Write-Host 'SNAPSHOT VERIFY: PASS' -ForegroundColor Green; exit 0 }
Write-Host ("SNAPSHOT VERIFY: {0} FAILURE(S)" -f $fail) -ForegroundColor Red
exit 1
