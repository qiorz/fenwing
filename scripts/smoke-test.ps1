param(
  [string]$Target = '192.168.1.2:38247',
  [int]$TimeoutSec = 40
)
$ErrorActionPreference = 'Continue'
$hdc = 'C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe'
$bundle = 'com.example.firefoxport'
$fail = 0
function Check([string]$name, [bool]$ok, [string]$detail = '') {
  if ($ok) { Write-Host ("PASS  {0} {1}" -f $name, $detail) -ForegroundColor Green }
  else { Write-Host ("FAIL  {0} {1}" -f $name, $detail) -ForegroundColor Red; $script:fail++ }
}
function Hdc([string]$cmd) { return (& $hdc -t $Target shell $cmd 2>&1 | Out-String) }

& $hdc tconn $Target 2>&1 | Out-Null
Hdc "aa force-stop $bundle" | Out-Null
Start-Sleep -Seconds 1
Hdc "hilog -w clear" | Out-Null
$startWall = Get-Date
Hdc "aa start -a EntryAbility -b $bundle --ps noresume 1" | Out-Null

# poll the log for first-composite and title (load signal)
$fcLine = $null
$titleSeen = $false
$deadline = (Get-Date).AddSeconds($TimeoutSec)
while ((Get-Date) -lt $deadline -and ($null -eq $fcLine -or -not $titleSeen)) {
  Start-Sleep -Seconds 2
  $log = Hdc "hilog -x | grep -E 'first-composite|title session=0 title=' | tail -6"
  $lines = $log -split "`n"
  foreach ($l in $lines) {
    if (-not $fcLine -and $l -match 'first-composite') { $fcLine = $l.Trim() }
    if ($l -match 'title session=0 title=') { $titleSeen = $true }
  }
  if ($null -ne $fcLine -and $titleSeen) { break }
}
Check 'first-composite' ($null -ne $fcLine) ($fcLine)
Check 'page loaded (title event)' $titleSeen

Start-Sleep -Seconds 2
Hdc "uitest uiInput longClick 1500 800" | Out-Null
Start-Sleep -Seconds 3
$menuLog = Hdc "hilog -x | grep -E 'menu shown' | tail -2"
Check 'context menu shown' ($menuLog -match 'menu shown')
Hdc "uitest uiInput click 1450 1400" | Out-Null

Start-Sleep -Seconds 2
$pidText = (Hdc "pidof $bundle").Trim()
Check 'process alive' ($pidText -match '^\d+$') $pidText

Write-Host ''
if ($fail -eq 0) { Write-Host 'SMOKE TEST: PASS' -ForegroundColor Green; exit 0 }
Write-Host ("SMOKE TEST: {0} FAILURE(S)" -f $fail) -ForegroundColor Red
exit 1
