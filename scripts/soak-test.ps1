param(
  [int]$Cycles = 6,
  [string]$OutDir = 'D:\ff-ohos\logs\soak'
)

$ErrorActionPreference = 'Continue'
$hdc = 'C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe'
$target = '192.168.1.2:38247'
$bundle = 'com.example.firefoxport'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$csv = Join-Path $OutDir 'soak.csv'
$crashes = Join-Path $OutDir 'crashes.log'
Remove-Item $csv, $crashes -ErrorAction SilentlyContinue

function Hdc([string]$cmd) {
  return (& $hdc -t $target shell $cmd 2>&1 | Out-String)
}
function Get-AppPid {
  $out = Hdc "pidof $bundle"
  $id = $out.Trim()
  if ($id -match '^\d+$') { return $id }
  return ''
}
function Get-Rss([string]$appPid) {
  if ([string]::IsNullOrEmpty($appPid)) { return -1 }
  $out = Hdc "ps -p $appPid -o pid,rss,vsz,comm"
  foreach ($line in ($out -split "`n")) {
    if ($line -match 'firefoxport') {
      $parts = ($line.Trim() -split '\s+')
      if ($parts.Count -ge 2 -and $parts[1] -match '^\d+$') { return [int]$parts[1] }
    }
  }
  return -1
}
function Get-MemAvail {
  $out = Hdc "cat /proc/meminfo"
  foreach ($line in ($out -split "`n")) {
    if ($line -match '^MemAvailable:\s+(\d+)') { return [int]$Matches[1] }
  }
  return -1
}
function Capture-Crash([string]$tag) {
  $fatal = Hdc "hilog -x | grep -E 'FATAL|SIGSEGV|SIGILL|SIGABRT' | tail -40"
  Add-Content -Path $crashes -Value "=== $tag $(Get-Date -Format o) ===" -Encoding UTF8
  Add-Content -Path $crashes -Value $fatal -Encoding UTF8
}

& $hdc tconn $target | Out-Null

$rows = @()
for ($i = 1; $i -le $Cycles; $i++) {
  Hdc "aa force-stop $bundle" | Out-Null
  Start-Sleep -Seconds 1
  $resume = ($i % 3 -eq 0)
  if ($resume) {
    Hdc "aa start -a EntryAbility -b $bundle" | Out-Null
  } else {
    Hdc "aa start -a EntryAbility -b $bundle --ps noresume 1" | Out-Null
  }
  Start-Sleep -Seconds 9

  $appPid = Get-AppPid
  $crashed = $false
  if ([string]::IsNullOrEmpty($appPid)) {
    $crashed = $true
    Capture-Crash "cycle$i-launch"
  }
  $rssLaunch = Get-Rss $appPid

  # open two more tabs
  & $hdc -t $target shell "uitest uiInput click 2483 1676" 2>&1 | Out-Null
  Start-Sleep -Seconds 3
  & $hdc -t $target shell "uitest uiInput click 2483 1676" 2>&1 | Out-Null
  Start-Sleep -Seconds 3
  $appPid = Get-AppPid
  $rssTabs = Get-Rss $appPid

  # switch between tabs
  & $hdc -t $target shell "uitest uiInput click 666 1673" 2>&1 | Out-Null
  Start-Sleep -Seconds 2
  & $hdc -t $target shell "uitest uiInput click 1100 1673" 2>&1 | Out-Null
  Start-Sleep -Seconds 2
  $appPid2 = Get-AppPid
  if ([string]::IsNullOrEmpty($appPid2)) {
    $crashed = $true
    Capture-Crash "cycle$i-switch"
  }
  $rssSwitch = Get-Rss $appPid2
  $memAvail = Get-MemAvail

  # navigation stress: focus address bar, type "x", Enter, wait for load
  & $hdc -t $target shell "uitest uiInput click 1200 425" 2>&1 | Out-Null
  Start-Sleep -Seconds 1
  & $hdc -t $target shell "uitest uiInput keyEvent 2040" 2>&1 | Out-Null
  Start-Sleep -Milliseconds 400
  & $hdc -t $target shell "uitest uiInput keyEvent 2054" 2>&1 | Out-Null
  Start-Sleep -Seconds 6
  $appPid3 = Get-AppPid
  if ([string]::IsNullOrEmpty($appPid3)) {
    $crashed = $true
    Capture-Crash "cycle$i-nav"
  }
  $rssNav = Get-Rss $appPid3

  # close the second tab and sample memory after reclamation
  & $hdc -t $target shell "uitest uiInput click 1185 1673" 2>&1 | Out-Null
  Start-Sleep -Seconds 2
  $rssClose = Get-Rss (Get-AppPid)
  $thresholdKb = 450000
  $overThreshold = ($rssNav -gt $thresholdKb)
  if ($overThreshold) {
    Add-Content -Path $crashes -Value "=== cycle$i rss over threshold: $rssNav KB ===" -Encoding UTF8
  }

  $rows += [pscustomobject]@{
    cycle = $i
    resume = $resume
    rss_launch_kb = $rssLaunch
    rss_tabs_kb = $rssTabs
    rss_switch_kb = $rssSwitch
    rss_nav_kb = $rssNav
    rss_close_kb = $rssClose
    mem_available_kb = $memAvail
    crashed = $crashed
    over_threshold = $overThreshold
  }
  Write-Output ("cycle {0}: launch={1}KB tabs={2}KB switch={3}KB nav={4}KB close={5}KB crashed={6} over={7}" -f $i, $rssLaunch, $rssTabs, $rssSwitch, $rssNav, $rssClose, $crashed, $overThreshold)
}

$rows | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8
$valid = $rows | Where-Object { $_.rss_launch_kb -gt 0 }
if ($valid.Count -gt 0) {
  $min = ($valid | Measure-Object rss_switch_kb -Minimum).Minimum
  $max = ($valid | Measure-Object rss_switch_kb -Maximum).Maximum
  $avg = [math]::Round(($valid | Measure-Object rss_switch_kb -Average).Average, 0)
  Write-Output ("SUMMARY cycles={0} rss_min={1}KB rss_max={2}KB rss_avg={3}KB crashes={4}" -f $Cycles, $min, $max, $avg, (($rows | Where-Object { $_.crashed }).Count))
}
