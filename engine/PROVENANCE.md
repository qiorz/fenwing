# 来源、归属与差异说明

## 1. 上游

- 项目：mozilla-central（Firefox / Gecko `142.0a1`）
- 基线提交：`5836a062726f715fda621338a17b51aff30d0a8c`（2025-07-08）
- 许可：MPL-2.0

本仓库不包含 Gecko 源码本身，只包含对它的一份补丁（diff）。

## 2. OHOS 移植层的来源

HarmonyOS/OpenHarmony 平台适配层并非从零开始，它站在社区工作之上：

- 社区项目：[`ohos_gecko-opensource`](https://gitcode.com/OpenHarmonyPCDeveloper/ohos_gecko-opensource)
  （gitcode，OpenHarmonyPCDeveloper），同样以 MPL-2.0 发布。
- 该项目的 README 描述了 `widget/openharmony`、`ports/ohos`、WebRender/EGL、
  `browser` chrome ArkTS 化等一整套平台层；本工程的内核树以它的 v271 适配层为蓝本，
  在 `5836a062` 基线上继续做了大量调试与功能修补。

**必须说清楚边界**：

- `engine/patches/firefox-ohos-gecko-5836a06272.patch` 是**本工程实际构建的那棵树**的完整快照，
  不是社区仓库的提交序列，也不代表社区的官方版本。
- 我们在尝试「社区补丁 + 本工程增量」的切分时发现：社区全量补丁是 CRLF 行尾，
  且其上下文与纯净 `5836a062` 已有漂移，无法干净 `git apply`。因此选择了整树补丁。
- 如果要追溯某个子系统「最初是谁写的」，请优先参考社区仓库；本仓库的补丁只保证
  「能复现我们构建出来的东西」。

## 3. 本工程的增量

**引擎侧（相对社区适配层）**

- `geckoview.js` 内容区菜单构造：刷新、复制链接、显示/隐藏工具栏、在新标签页打开链接、
  保存图片、复制图片地址、复制页面地址/标题（通过 `airweb-tab-state` 信封回传 ArkTS）；
- 标题 / URL / 下载 / 菜单回调契约修正，`--airweb-force-no-jit` 开关，JIT 探测与自动降级；
- `omni.ja` 目录形式传参、`libgeckoxcomp.so` 去 build-id、自建 `libz.so`；
- `omni.ja` 打包改为 deflate（体积 65.5 → 20.4 MB）。

**应用侧（Fenwing）**

- P0：`SessionStore` 防抖落盘、异常退出判定、20 s 加载看门狗、ArkTS 错误覆盖层，
  恢复横幅携带「上次停留 URL」；
- P1：下载回调与横幅、`DocumentViewPicker`（URI → 沙箱路径）、全屏外壳隐藏、
  页内查找、整页缩放；
- P1.5：地址栏单行 + 底栏三行压两行（内容区 +80–100 vp）、原生菜单浮层
  （子菜单/勾选/快捷键/禁用态/锚点定位）；
- P2：新标签打开链接、保存图片、下载「打开/清空」、引擎驱动的历史记录、
  地址栏历史/书签补全；
- P3：`build-all` / `verify-snapshot` / `install-device` / `smoke-test` / `soak-test`
  与本地 CI；
- P4：去 Firefox 品牌（AirWeb → Fenwing）、随包许可三件套、权限与隐私说明。

## 4. 二进制产物

`Releases` 里的 `fenwing-engine-1.2.0.zip` 由上述树编译：

| 文件 | 说明 |
|---|---|
| `libxul.so` (185 MB) | Gecko 主库，strip 后、带 `.permission`（JIT 版） |
| `libgeckoview.so` | OHOS 平台层 |
| `libgeckoxcomp.so` | 同一 NAPI 模块副本，去掉 build-id 供 XComponent 触发注册 |
| `libmozjs*.so` / NSS / NSPR / gkcodecs … | 运行时依赖（全量 strip） |
| `omni.ja` (20.4 MB) | GRE 资源包（deflate） |

MPL-2.0 对二进制分发的要求是「提供对应源码的获取方式」——本仓库的 `engine/` + 
[`docs/SOURCE-OFFER.md`](../docs/SOURCE-OFFER.md) 满足这一点：基线提交公开可得，补丁在本仓库内。

## 5. 商标与更名

“Firefox”“Gecko”“Mozilla” 是 Mozilla Foundation 的商标。本项目原名
“Firefox for HarmonyOS”，2026-11-18 按 Mozilla 商标政策去掉 Firefox 品牌；先定名 AirWeb，
因与既有项目重名，同日改用 **Fenwing**：
应用名、窗口标题、界面文案不再使用 Firefox 品牌，仅保留“基于 Gecko 142”的技术事实描述。
Fenwing 与 Mozilla 无隶属、赞助或背书关系，产物不随附任何 Mozilla 品牌资源。
