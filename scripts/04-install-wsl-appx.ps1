# 04-install-wsl-appx.ps1 — 非管理员运行
# 作用：按用户安装从 GitHub 下载的 WSL MSIX bundle（无需管理员），并验证 wsl.exe 可用。
# 日志：D:\ff-ohos\logs\04-wsl-appx.log
$ErrorActionPreference = 'Continue'
$log = 'D:\ff-ohos\logs\04-wsl-appx.log'
New-Item -ItemType Directory -Path 'D:\ff-ohos\logs' -Force | Out-Null
Start-Transcript -Path $log -Force | Out-Null
"TIME: " + (Get-Date -Format o)

$msix = 'D:\ff-ohos\setup\Microsoft.WSL_3.0.5.0_x64_ARM64.msixbundle'
"file: $msix  size=$([math]::Round((Get-Item $msix).Length/1MB,1)) MB"

"=== Add-AppxPackage (per-user) ==="
try {
    Add-AppxPackage -Path $msix -ErrorAction Stop
    "APPX_INSTALL=OK"
} catch {
    "APPX_INSTALL_FAILED: $($_.Exception.Message)"
}

"=== appx list ==="
Get-AppxPackage | Where-Object { $_.Name -match 'WindowsSubsystemForLinux|WSL' } |
    Select-Object Name,Version,Status,InstallLocation | Format-List | Out-String

"=== wsl.exe (System32 stub / app alias) ==="
& wsl.exe --version 2>&1 | Out-String
"WSL_VERSION_EXIT=$LASTEXITCODE"
$alias = "$env:LOCALAPPDATA\Microsoft\WindowsApps\wsl.exe"
"alias exists: $(Test-Path $alias)"
if (Test-Path $alias) { & $alias --version 2>&1 | Out-String }

"SCRIPT-DONE"
Stop-Transcript | Out-Null
