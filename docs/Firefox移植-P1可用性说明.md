# Firefox / Gecko for HarmonyOS —— P1 可用性实现与验证

> 完成时间：2026-11-17
> 设备：HUAWEI MatePad Edge QXS-W00（HarmonyOS 7.0.0.111 / API 26）

## 一、本轮实现

| 功能 | 实现 | 状态 |
|---|---|---|
| 下载 | `registerDownloadCallback` → AppStorage → 顶部横幅（开始/进度/完成/失败）+ 下载记录落库（`upsertDownload`） | ✅ 真机通过 |
| 文件选择 | `registerFilePickerCallback` → `DocumentViewPicker` → 复制到沙箱 → `resolveFilePicker(id, 0, path)` | ✅ 真机通过 |
| 全屏 | `registerFullscreenCallback` → 隐藏浏览器外壳（地址栏/标签栏）+ 系统栏 best-effort；`exitFullscreen` 恢复 | ✅ 真机通过 |
| 页内查找 | 查找栏 + `findInPage(query, backward, matchCase)` | ✅ 真机通过 |
| 缩放 | 工具栏 −/100%/+ → `setFullZoom()` | ✅ 真机通过 |

## 二、真机验证证据

### 下载
```
BrowserPage: download event: 开始下载：hello.txt
BrowserPage: download event: 下载完成：/data/storage/el2/base/haps/entry/files/Downloads/hello.txt
```
（由页面内 `Blob` + `a[download]` 触发，走 Gecko `nsExternalAppHandler` 真实下载链路）

### 文件选择
```
BrowserPage: picker returned 1 uris
GeckoViewBoot: resolveFilePicker id=1 result=0
FirefoxBridge: [FilePicker] ResolveFilePicker cbId=1 result=0
  path=/data/storage/el2/base/haps/entry/cache/picked_..._env-probe.txt
```
页面 `<input type=file>` 从 "No file selected" 变为显示选中文件名。

### 全屏
- 点击「全屏测试」（`documentElement.requestFullscreen()`）→ `RegisterFullscreenCallback` 触发 → 地址栏/标签栏隐藏，页面占满窗口，右上出现「退出全屏」；
- 点击「退出全屏」→ `GeckoBridge_ExitFullscreen` → 外壳恢复。
- 注：2in1 窗口形态下 `setWindowLayoutFullScreen` 返回 "device not support"，因此全屏以“隐藏浏览器外壳 + 尽力隐藏系统栏”实现。

### 查找 / 缩放
```
GeckoViewBoot: findInPage link
GeckoViewBoot: setFullZoom ...
```
UI 缩放比例 100% → 90% 生效。

## 三、过程中修掉的两个关键问题

### 1) HSP 增量安装不生效（重要基础设施问题）
- 现象：代码已改、HSP 已重新打包，但设备上仍运行旧 `GeckoViewBoot`/`libgeckoview`，新方法（`setFullZoom`、`getSessionHistory`）在 ArkTS 里报 `undefined`。
- 根因：`bm install -r` 在 HSP 版本号不变时会保留旧副本，没有替换 HSP。
- 解决：`bm uninstall com.example.firefoxport` 后重新安装 HAP+HSP。
- 约定：**以后改动 gecko 模块（HSP 的 ets/native）必须卸载重装**，或提升 versionCode。

### 2) Picker 返回 URI 不是本地路径
- 系统 Picker 返回 `file://docs/storage/...` 形式的 URI，直接去掉 `file://` 会得到相对路径，Gecko 无法 `InitWithNativePath`。
- 修复：用 `fileIo` 打开 URI 并把文件复制到应用沙箱 `cacheDir`（保留原文件名），再把沙箱绝对路径回填给 Gecko。

### 3) 看门狗误报（顺带）
- `file://` 页面收不到 `pageLoad=stop`，导致 20s 后误显示"加载失败"。
- 修复：URL/标题回调也视为加载完成，解除看门狗。

## 四、已知限制 / 后续

1. 下载保存到应用沙箱 `Downloads/`，尚无"另存为"与完成通知点击打开；
2. Picker 复制到缓存后未做清理（长期使用需按容量淘汰）；
3. 全屏不改变 OS 窗口边框（2in1 窗口模式限制）；
4. 页内查找无结果计数/高亮统计（port 未提供回调）；
5. 菜单/右键菜单（`registerMenuCallback`/`resolveMenuCommand`）尚未接入；
6. 长按/右键菜单后需要抑制 XUL popup 的 ArkTS 菜单浮层，建议作为独立 P1.5 任务。

## 五、调试入口（不影响正常使用）

```
--ps demo 1       加载 P1 演示页（file input / 下载 / 全屏按钮）
--ps perf 1       基准页
--ps nojit 1      强制解释器
--ps url <url>    覆盖启动页
--ps noresume 1   跳过会话恢复
```
