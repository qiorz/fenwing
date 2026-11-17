# Firefox / Gecko for HarmonyOS —— 项目审视与下一步计划

> 审视时间：2026-11-17　设备：MatePad Edge（API 26 / tablet）
> 产物：HAP 0.5 MB + HSP ≈ 292 MB（含 libxul 185 MB、omni.ja 65 MB）

## 一、当前已经打通的能力

| 能力 | 状态 | 关键实现 |
|---|---|---|
| Gecko 内核在设备沙箱内启动 | ✅ | `libxul.so` dlopen + `XRE_main`，GRE=omni.ja |
| 页面渲染（WebRender/EGL） | ✅ | XComponent(SURFACE) + `libgeckoxcomp.so` |
| 触摸 / 鼠标 / 键盘输入 | ✅ | XComponent 原生回调 → `GeckoBridge_Dispatch*` |
| IME 软键盘 + 文字入库 | ✅ | `registerIMECallback` + 隐藏 TextInput + 增量 `insertText` |
| 真实网络（HTTPS） | ✅ | `ohos.permission.INTERNET` |
| 真·多标签会话 | ✅ | `createSession/switchToSession/closeSession` + `forceRepaint` |
| 标签标题 / 地址栏同步 | ✅ | geckoview.js DOMTitleChanged → `airweb-tab-state` → ArkTS |
| 前进 / 后退 | ✅ | ArkTS 每标签 URL 栈 + `loadUrlForSession` |
| JIT（ACL） | ✅ | ACL + `.permission` 段 + 自动探测 |
| 构建/签名/安装 | ✅ | 全命令行 hvigor + 自动签名，可重复 |

性能数据见《Firefox移植-性能基线报告.md》：JIT 相比解释器在计算密集 JS 上有 **14–38×** 提升。

## 二、架构与关键约束

```
EntryAbility (ArkTS)
 └─ libgeckoview.so (NAPI, 社区 geckoview.cpp)
     └─ libxul.so (Gecko 142, 单进程, no-e10s)
         ├─ omni.ja (GRE 资源, 运行时从 HSP rawfile 复制到沙箱)
         ├─ libgeckoxcomp.so (XComponent 回调副本)
         └─ NSS/NSPR/ffvpx 等 14 个依赖库
BrowserPage (ArkTS 浏览器壳: 地址栏/标签栏/书签/历史/下载/设置)
```

- **单进程、单 EGL Surface**：port 的 `OHOSForceRepaint.cpp` 已注明这是硬约束——整个进程只有一个渲染目标，多 `<browser>` 需要 `docShellIsActive` 切换 + `SetIsActive` toggle 才能出帧（我们已用 ForceRepaint 解决）。
- **geckoview.js 的 startupCache**：profile 里缓存编译后的 chrome JS，改 omni.ja 后必须让它失效（我们按 omni.ja 内容 stamp 条件清理）。
- **JIT 依赖 ACL**：没有 ACL 时 RWX 映射"成功"但执行 SIGILL，必须走坚盾降级解释器。
- **no-e10s**：内容进程拉不起来，所有页面在主进程；单页面崩溃 = 整 App 崩溃。

## 三、主要风险 / 技术债

| 类别 | 问题 | 影响 |
|---|---|---|
| 稳定性 | 无崩溃隔离（单进程）、无崩溃恢复/会话恢复 | 页面 Crash 会带崩整个浏览器 |
| 稳定性 | 页面 OOM、网络错误、证书错误无友好页 | 用户看到白屏/卡死 |
| 功能 | 下载、文件选择、全屏视频、菜单/右键、页内查找、缩放、打印 | 只完成回调注册，宿主 UI 未接 |
| 功能 | 扩展、书签/历史与引擎联动、密码/自动填充 | 壳层有 UI，未接引擎 |
| 性能 | 冷启动 ~400ms（JIT）~370ms（解释器）已可接受；首屏网络路径未专项优化 | 可再优化 |
| 体积 | HSP 292 MB（libxul 185 MB 已 strip） | 分发/安装耗时、存储占用 |
| 工程 | 无 CI、无自动化回归；诊断日志/临时钩子曾多次引入 | 修改易回退，验证靠手工 |
| 合规 | **Firefox 商标/Logo 不可用于第三方发行**；MPL-2.0 需保留声明与源码获取方式 | 若要公开分发必须处理 |

## 四、下一步优先级建议

### P0｜稳定性（最该先做）
1. **崩溃捕获与恢复**：接入 `MOZ_CRASHREPORTER`/minidump 或 `faultloggerd` 回调；App 侧捕获后重启引擎并恢复标签 URL；
2. **错误页**：网络失败/证书错误/进程崩溃显示可读错误页（ArkTS 外壳层或 `about:neterror`）；
3. **标签崩溃隔离**：中期评估能否把每个 `<browser>` 放进独立 content 进程（需要 e10s 在 OHOS 可用，当前 port 明确不可行，需先解决子进程启动）。

### P1｜可用性（让"能用"变成"好用"）
1. 下载链路：`registerDownloadCallback` → 系统下载/文件保存 UI；
2. 文件选择：`registerFilePickerCallback` → 系统 Picker；
3. 全屏视频：`registerFullscreenCallback` → 窗口/系统栏；
4. 菜单/右键：`registerMenuCallback` + `NativeMenuOverlay`；
5. 页内查找、缩放、打印、剪贴板、桌面模式切换（port 已有对应 NAPI，逐个接壳层）；
6. 地址栏搜索建议、书签/历史点击直接 `loadUrlForSession`。

### P2｜性能与体积
1. 冷启动：延迟加载非首屏模块、omni.ja 常驻缓存、profile 预热；
2. 页面加载：DNS 预解析、连接复用、HTTP/2/3（NSS 已具备）、预加载；
3. JIT 调参：`javascript.options.*`（Warp/Ion 预热、Ion 编译阈值）、WASM JIT 路径验证；
4. 体积：libxul 按需裁剪（`--disable-*`）、依赖库 strip、omni.ja 压缩策略、按 ABI/设备拆分 HSP。

### P3｜工程化
1. 建立 CI（Linux 构建 + 可选真机冒烟），产物版本化；
2. 固化"改动 → 构建 → 安装 → 冒烟"脚本（本轮用的一堆 patch 脚本应收敛成一套幂等脚本）；
3. 回归清单：启动/首帧、页面加载、输入、IME、多标签、前进后退、标题、JIT 开关；
4. 文档：构建环境（WSL/SDK/NDK 版本）、签名材料与 ACL 申请流程、已知问题。

### P4｜合规与分发（若要给别人用）
1. 替换 Firefox 名称/Logo（Mozilla 商标政策）；
2. 保留 MPL-2.0 声明、提供对应源码与修改说明；
3. 第三方库许可清单（NSS/NSPR/libvpx/ffmpeg 等）；
4. 若上架：ACL 权限需按应用市场要求提交场景说明（我们已具备"适配坚盾模式"的降级路径）。

## 五、建议的下一步（具体动作）

1. **本周**：完成下载 + 文件选择 + 全屏三条宿主链路（port NAPI 已就绪，主要是 ArkTS UI 与系统 Picker/下载管理器对接）；
2. **随后**：崩溃捕获 + 错误页 + 标签恢复，建立最小可用稳定性闭环；
3. **再后**：体积优化（目标 HSP < 200 MB）与启动优化；
4. **最后**：CI 与合规整理，形成可交付版本。

> 备注：当前所有改动集中在 `D:\ff-ohos\scripts\` 与工程 `entry/gecko` 源码；建议尽快把这些 patch 合并进一份"干净可构建"的工程快照（目前是增量 patch 方式），避免后续维护成本继续上升。
