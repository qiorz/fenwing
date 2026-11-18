# Fenwing 隐私说明

> 版本：1.2.0 · 更新：2026-11-18
> 适用：Fenwing（HarmonyOS / OpenHarmony arm64，包名 `com.example.firefoxport`）的侧载、
> 内测与企业分发版本。

## 一句话

**Fenwing 不收集、不上传任何用户数据**：没有遥测、没有崩溃自动上报、没有账号系统，
浏览记录只存在你的设备上。

## 我们处理哪些数据、存在哪

| 数据 | 存放位置 | 用途 | 是否上传 |
|---|---|---|---|
| 浏览历史、书签 | 应用沙箱内数据库（`BrowserDatabase`） | 历史面板、地址栏补全 | 否 |
| 下载记录与文件 | 应用沙箱 `files/Downloads/` | 下载管理 | 否 |
| 标签会话 | 沙箱内 `session.json` | 异常退出后的会话恢复 | 否 |
| 站点数据 / Cache / Cookie | Gecko profile 目录 | 正常浏览 | 否（仅随网页请求发往你访问的站点） |
| 调试日志 | 仅本地 hilog | 开发排障 | 否 |

**不会发生的事**：不采集设备标识、不读取通讯录/相册/位置、不注入广告、不做行为分析、
不在后台向任何服务器发起请求（除你主动访问的网页本身及其子资源）。

## 权限与用途

| 权限 | 用途 | 说明 |
|---|---|---|
| `ohos.permission.INTERNET` | 加载网页 | 唯一与网络相关的权限 |
| `ohos.permission.kernel.ALLOW_WRITABLE_CODE_MEMORY` | JS JIT 需要可写可执行内存 | 仅影响本应用进程，不修改系统 |
| `ohos.permission.kernel.DISABLE_CODE_MEMORY_PROTECTION` | 配合 JIT | 同上 |

两条 `kernel.*` 属于 ACL 权限：没有带 ACL 的签名时，应用仍可运行，但引擎会降级为解释器模式。

## 文件与剪贴板

- 文件选择通过系统 Picker，仅在用户授权后读取所选文件，并复制到应用沙箱缓存；
- 下载只写入应用沙箱；
- 「复制链接 / 复制图片地址」会写入系统剪贴板——这是你主动触发的操作。

## 第三方组件

Fenwing 包含 Gecko（MPL-2.0）、FFmpeg（LGPL-2.1+，动态链接）、libvpx（BSD-3-Clause）等组件，
详见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。这些组件本身不含遥测；Gecko 的
telemetry/crashreporter 在本构建中已关闭（`--disable-crashreporter`，未接入 telemetry 服务）。

## 变更与联系

隐私说明随版本更新，历史版本见仓库提交记录。问题请开 Issue：
<https://github.com/qiorz/fenwing/issues>。

> 本文不构成法律意见；正式上架前请按发行地区法规复核。
