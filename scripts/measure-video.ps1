param(
  [string]$Label = 'hw',
  [int]$Samples = 6,
  [string]$Target = '192.168.1.2:38247'
)
$ErrorActionPreference = 'Continue'
$hdc = 'C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe'
$bundle = 'com.example.firefoxport'

& $hdc tconn $Target 2>&1 | Out-Null
& $hdc -t $Target shell "power-shell wakeup" 2>&1 | Out-Null
& $hdc -t $Target shell "aa force-stop $bundle" 2>&1 | Out-Null
& $hdc -t $Target shell "aa start -a EntryAbility -b $bundle --ps demo 1 --ps noresume 1" 2>&1 | Out-Null
Start-Sleep -Seconds 20
$appPid = (& $hdc -t $Target shell "pidof $bundle" 2>&1).Trim()
if ($appPid -notmatch '^\d+$') {
  Write-Host "LAUNCH FAILED (pid=$appPid)" -ForegroundColor Red
  exit 1
}
$rss = (& $hdc -t $Target shell "ps -p $appPid -o pid,rss,vsz,comm" 2>&1 | Select-String 'firefoxport').Line
Write-Host "label=$Label pid=$appPid"
Write-Host $rss.Trim()
$cpus = @()
for ($i = 0; $i -lt $Samples; $i++) {
  $line = (& $hdc -t $Target shell "top -b -n 1 -p $appPid | tail -2" 2>&1 | Select-String 'firefoxport').Line
  if ($line) {
    $parts = ($line.Trim() -split '\s+')
    $cpus += [double]$parts[8]
    Write-Host ("sample {0}: {1}" -f $i, $line.Trim())
  }
  Start-Sleep -Seconds 2
}
if ($cpus.Count -gt 0) {
  $avg = [math]::Round(($cpus | Measure-Object -Average).Average, 1)
  Write-Host ("SUMMARY {0}: cpu_avg={1}% cpu_min={2}% cpu_max={3}% rss={4}" -f $Label, $avg, ($cpus | Measure-Object -Minimum).Minimum, ($cpus | Measure-Object -Maximum).Maximum, $rss.Trim())
}
