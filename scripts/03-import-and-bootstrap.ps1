# 03-import-and-bootstrap.ps1 — 非管理员运行
# 前提：WSL 本体（MSIX）已装好、wsl.exe 可用；Ubuntu rootfs 已下载到 D:\ff-ohos\setup
# 作用：导入 Ubuntu-24.04 → 修 DNS/systemd 冲突 → 跑 02-wsl-bootstrap.sh（建 dev 用户、装依赖、Rust）
# 日志：D:\ff-ohos\logs\03-import.log
$ErrorActionPreference = 'Continue'
$log = 'D:\ff-ohos\logs\03-import.log'
New-Item -ItemType Directory -Path 'D:\ff-ohos\logs' -Force | Out-Null
Start-Transcript -Path $log -Force | Out-Null
"TIME: " + (Get-Date -Format o)

$Distro    = 'Ubuntu-24.04'
$Rootfs    = 'D:\ff-ohos\setup\noble-server-cloudimg-amd64-root.tar'
$InstallDir= 'D:\WSL\Ubuntu2404'
$Bootstrap = '/mnt/d/ff-ohos/scripts/02-wsl-bootstrap.sh'

"=== wsl --version ==="
& wsl.exe --version 2>&1 | Out-String
"=== wsl --set-default-version 2 ==="
& wsl.exe --set-default-version 2 2>&1 | Out-String

"=== import (if absent) ==="
$list = (& wsl.exe -l -q 2>&1 | Out-String)
if ($list -notmatch [regex]::Escape($Distro)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    & wsl.exe --import $Distro $InstallDir $Rootfs --version 2 2>&1 | Out-String
    "IMPORT_EXIT=$LASTEXITCODE"
} else {
    "already installed: $Distro"
}

"=== fix resolv.conf conflict + wsl.conf ==="
& wsl.exe -d $Distro -u root -- bash -lc "rm -f /etc/resolv.conf; printf '[network]\ngenerateResolvConf = true\n[interop]\nappendWindowsPath = false\n' > /etc/wsl.conf; cat /etc/wsl.conf"
& wsl.exe --terminate $Distro 2>&1 | Out-String
Start-Sleep -Seconds 3

"=== copy bootstrap script ==="
& wsl.exe -d $Distro -u root -- cp $Bootstrap /tmp/02-wsl-bootstrap.sh 2>&1 | Out-String
& wsl.exe -d $Distro -u root -- chmod +x /tmp/02-wsl-bootstrap.sh 2>&1 | Out-String

"=== run bootstrap (this takes several minutes) ==="
& wsl.exe -d $Distro -u root -- bash /tmp/02-wsl-bootstrap.sh 2>&1 | Out-String

"=== verify ==="
& wsl.exe -d $Distro -u dev -- bash -lc "python3 --version; python3.11 --version 2>/dev/null; rustc --version; cargo --version; rustup target list --installed; clang --version | head -1; cmake --version | head -1; ninja --version" 2>&1 | Out-String

"SCRIPT-DONE"
Stop-Transcript | Out-Null
