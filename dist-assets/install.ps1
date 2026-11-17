# Firefox for HarmonyOS — 引擎二进制安装脚本（Windows / PowerShell）
#
# 用法：把本压缩包解到任意目录，然后：
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -AppPath D:\path\to\firefox-ohos\app
#
# 它会把你下载的引擎产物按 app/ 目录期望的位置铺好。

param(
    [Parameter(Mandatory = $true)][string]$AppPath
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$app = (Resolve-Path $AppPath).Path

if (-not (Test-Path "$app\gecko")) { throw "$app 看起来不是 firefox-ohos 的 app/ 目录（找不到 gecko/）" }

Write-Host "[1/4] 运行时库 -> app\gecko\libs\arm64-v8a"
New-Item -ItemType Directory -Force "$app\gecko\libs\arm64-v8a" | Out-Null
Copy-Item "$here\gecko\libs\arm64-v8a\*" "$app\gecko\libs\arm64-v8a\" -Force -Recurse

Write-Host "[2/4] NAPI 链接用库 -> app\gecko\src\main\libs\arm64-v8a"
New-Item -ItemType Directory -Force "$app\gecko\src\main\libs\arm64-v8a" | Out-Null
Copy-Item "$here\gecko\src\main\libs\arm64-v8a\*" "$app\gecko\src\main\libs\arm64-v8a\" -Force -Recurse
Copy-Item "$app\gecko\libs\arm64-v8a\libxul.so" "$app\gecko\src\main\libs\arm64-v8a\libxul.so" -Force

Write-Host "[3/4] GRE 资源 -> app\gecko\src\main\resources\rawfile\omni.ja"
Copy-Item "$here\gecko\src\main\resources\rawfile\omni.ja" "$app\gecko\src\main\resources\rawfile\omni.ja" -Force

Write-Host "[4/4] 完成。现在用 DevEco Studio 打开 app\ 并构建（记得配置签名）。"
