# 01-install-wsl-elevated.ps1  —  重启后由用户点 UAC「是」后以管理员运行
# 作用：安装 WSL 本体 + Ubuntu 24.04（不自动启动，避免交互式建用户），并设定默认 WSL2。
# 日志：D:\ff-ohos\logs\01-install-wsl.log
$ErrorActionPreference = 'Continue'
$log = 'D:\ff-ohos\logs\01-install-wsl.log'
New-Item -ItemType Directory -Path 'D:\ff-ohos\logs' -Force | Out-Null
Start-Transcript -Path $log -Force | Out-Null
"WHOAMI: " + (whoami)
"TIME: " + (Get-Date -Format o)

"=== wsl --install -d Ubuntu-24.04 --no-launch ==="
& wsl.exe --install -d Ubuntu-24.04 --no-launch 2>&1 | Out-String
"WSL_INSTALL_EXIT=$LASTEXITCODE"

"=== wsl --set-default-version 2 ==="
& wsl.exe --set-default-version 2 2>&1 | Out-String
"SET_DEFAULT_EXIT=$LASTEXITCODE"

"=== wsl --update ==="
& wsl.exe --update 2>&1 | Out-String
"UPDATE_EXIT=$LASTEXITCODE"

"=== wsl -l -v ==="
& wsl.exe -l -v 2>&1 | Out-String

"SCRIPT-DONE"
Stop-Transcript | Out-Null
