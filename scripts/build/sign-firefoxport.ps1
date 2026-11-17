# sign-firefoxport.ps1 — 用 AGC 调试证书/Profile 离线签名 HAP/HSP（不依赖 HO-Kit）
# 用法：
#   .\sign-firefoxport.ps1 -InFile <unsigned.hap> -OutFile <signed.hap>
# 需要把 AGC 下载的两份材料放到 D:\ff-ohos\signing\：
#   firefoxport.cer  （调试证书）
#   firefoxport.p7b  （调试 Profile，bundleName=com.example.firefoxport，含本机 UDID）
param(
    [Parameter(Mandatory)][string]$InFile,
    [Parameter(Mandatory)][string]$OutFile
)
$ErrorActionPreference = 'Continue'
$ever   = 'C:\Program Files\Huawei\DevEco Studio'
$java   = "$ever\jbr\bin\java.exe"
$tool   = "$ever\sdk\default\openharmony\toolchains\lib\hap-sign-tool.jar"
$sign   = 'D:\ff-ohos\signing'
$pwd    = 'Foxport#2026'
$cer    = "$sign\firefoxport.cer"
$p7b    = "$sign\firefoxport.p7b"
$p12    = "$sign\firefoxport.p12"

foreach ($f in @($java,$tool,$cer,$p7b,$p12)) {
    if (-not (Test-Path $f)) { Write-Host "MISSING: $f" -ForegroundColor Red; exit 2 }
}
Write-Host "signing $InFile -> $OutFile" -ForegroundColor Cyan
& $java -jar $tool sign-app `
    -keyAlias debugKey `
    -signAlg SHA256withECDSA `
    -mode localSign `
    -appCertFile $cer `
    -profileFile $p7b `
    -inFile $InFile `
    -keystoreFile $p12 `
    -outFile $OutFile `
    -keyPwd $pwd `
    -keystorePwd $pwd 2>&1 | Out-String
$rc = $LASTEXITCODE
Write-Host "SIGN_EXIT=$rc"
if ($rc -eq 0) {
    Write-Host "--- verify ---" -ForegroundColor Cyan
    & $java -jar $tool verify-app -inFile $OutFile -outCertChain "$sign\verify-chain.cer" -outProfile "$sign\verify-profile.p7b" 2>&1 | Out-String
}
