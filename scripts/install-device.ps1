param(
  [string]$Target = '192.168.1.2:38247',
  [switch]$Reinstall,
  [switch]$ForceHsp
)
$ErrorActionPreference = 'Stop'
$hdc = 'C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe'
$bundle = 'com.example.firefoxport'
$proj = 'D:\ff-ohos\work\firefoxport'
$hap = Join-Path $proj 'entry\build\default\outputs\default\entry-default-signed.hap'
$hspPath = Join-Path $proj 'gecko\build\default\outputs\default\gecko-default-signed.hsp'

& $hdc tconn $Target 2>&1 | Out-Null
if (-not (Test-Path $hap)) { throw "HAP not found: $hap (run build-all.ps1)" }
if (-not (Test-Path $hspPath)) { throw "HSP not found: $hspPath (run build-all.ps1)" }

& $hdc -t $Target shell "aa force-stop $bundle" 2>&1 | Out-Null
& $hdc -t $Target file send $hap /data/local/tmp/entry-signed.hap 2>&1 | Out-Null
& $hdc -t $Target file send $hspPath /data/local/tmp/gecko-signed.hsp 2>&1 | Out-Null

if ($Reinstall -or $ForceHsp) {
  & $hdc -t $Target shell "bm uninstall -n $bundle" 2>&1 | Out-Null
  $out = & $hdc -t $Target shell "bm install -p /data/local/tmp/entry-signed.hap /data/local/tmp/gecko-signed.hsp" 2>&1
} else {
  $out = & $hdc -t $Target shell "bm install -r -p /data/local/tmp/entry-signed.hap /data/local/tmp/gecko-signed.hsp" 2>&1
}
Write-Host ($out -join "`n")
if (($out -join "`n") -match 'successfully') {
  Write-Host "INSTALL OK" -ForegroundColor Green
  exit 0
}
Write-Host "INSTALL FAILED" -ForegroundColor Red
exit 1

