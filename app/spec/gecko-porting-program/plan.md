# Implementation Plan: Gecko for HarmonyOS 完整移植工程

**Input**: Feature specification from `/storage/Users/currentUser/Documents/DevEcoStudioProjects/firefoxport/spec/gecko-porting-program/spec.md`

**Note**: 本计划以现有 `firefoxport` HarmonyOS 工程为集成外壳，定义 Gecko 移植的技术路线、模块边界、构建管线、接口契约、里程碑与 Go/No-Go 门禁。

## Summary

将 Firefox 的 Gecko 引擎完整移植到 HarmonyOS（API 26，aarch64），最终形成可日常使用的 Firefox 浏览器。工程采用三层边界：

1. **`entry`**：ArkTS 浏览器 UI、Ability、页面路由、用户数据展示。
2. **`gecko`**：HarmonyOS Native 动态共享包（HSP），承载 NAPI 桥接、Gecko 嵌入层、预编译 `.so` 打包。
3. **`third_party/gecko` + `build/gecko`**：Gecko 上游源码、补丁、out-of-tree 构建产物，不参与 DevEco 的 ArkTS 编译索引。

技术路线：本机原生 aarch64-ohos 工具链（clang 15/22、Rust 1.99、CMake/Ninja/Python）优先；JIT 以解释器模式为先；进程模型以单进程为先；图形以 XComponent + EGL/GLES 为先，软件渲染（SWGL）为兜底；所有可执行代码通过 HAP 内嵌 `.so` 加载，不依赖独立二进制执行。

本计划的交付物是**可执行的架构与实施计划**。Phase 0 先验证 HAP + NAPI + Rust/SpiderMonkey 最小链路，再进入 Gecko 图形、网络与 UI 里程碑。

## Technical Context

**Language/Version**: ArkTS（API 26）；C++（以 Gecko 基线要求的 C++ 标准为准）；Rust 1.99.1（host `aarch64-unknown-linux-ohos`）；Python 3.12.10。

**Primary Dependencies**: Firefox/Gecko 源码（最新 ESR，M0 锁定具体版本）、SpiderMonkey、NSPR、NSS、WebRender、Necko；HarmonyOS NDK（clang 15.0.4、sysroot、EGL/GLES/Vulkan、NAPI、ACE）；Homebrew LLVM 22.1.8 + LLD 22.1.8（keg-only）；CMake 3.28.2；Ninja 1.13.2；Node 26.10；DevEco Studio / hvigor。

**State Management**: 浏览器 UI 为 greenfield，采用 HarmonyOS State Management V2；Native 引擎状态不进入 ArkTS 状态树，通过 NAPI 事件与 ArkTS facade 同步。

**Storage**: `Preferences` 存设置；`RelationalStore` 存书签、历史、下载记录；Gecko profile 存 cookie、缓存、IndexedDB 等；账户密钥使用 HUKS/Asset Store，不以明文落盘。

**Testing**: hvigor/DevEco 构建验证；ArkTS hypium 单元测试；NAPI 冒烟测试；SpiderMonkey JS shell 测试；Gecko reftest/mochitest 子集；真机安装、启动、渲染、网络、崩溃恢复测试。

**Target Platform**: HarmonyOS API 26（Release），tablet / 2in1，aarch64；首要设备 HUAWEI MatePad Edge。

**Project Type**: HarmonyOS 移动应用 + Native 引擎动态共享包（HSP）。

**Performance Goals**: Phase 0 目标为 JS 求值往返 < 50ms、静态 HTML 首帧 < 5s、单标签内存 < 1.5GB、30 分钟无崩溃；产品目标为 60fps 滚动、热启动页面 < 2s、5 标签内存 < 2GB。上述为目标值，需在 M0-M3 逐项实测校准。

**Constraints**: 系统不提供第三方 WebView 内核接入位；JIT 默认关闭，需受限 ACL 审批；普通应用禁止 fork/exec；自定义可执行文件在可写目录运行返回 EPERM；HAP/HSP 必须签名；本机 16 核 / 16GB 内存 / 约 119GB 可用磁盘；全量 Gecko 构建建议外部 Linux CI。

**Scale/Scope**: Gecko 为千万行级 C++ 代码库；涉及构建、运行时、JS、图形、网络、进程、安全、媒体、UI、同步十条主线；产品级移植为多年工程，Phase 0 POC 为 6-12 个月量级。

## Project Structure

### Documentation (this feature)

```text
/storage/Users/currentUser/Documents/DevEcoStudioProjects/firefoxport/spec/gecko-porting-program/
├── spec.md              # 需求规格
├── plan.md              # 本文件
└── tasks.md             # Phase 3 生成
```

### Source Code (repository root)

```text
/storage/Users/currentUser/Documents/DevEcoStudioProjects/firefoxport/
├── AppScope/
│   └── app.json5
├── entry/                                  # HAP：ArkTS 浏览器 UI + Ability
│   ├── build-profile.json5
│   ├── oh-package.json5
│   └── src/main/
│       ├── module.json5
│       ├── ets/
│       │   ├── entryability/
│       │   ├── pages/                      # 页面装配
│       │   ├── views/                      # 浏览器业务视图
│       │   ├── components/                 # 通用 UI 组件
│       │   ├── viewmodel/                  # UI 状态与事件编排
│       │   ├── model/                      # 领域模型
│       │   ├── service/                    # 引擎/下载/同步服务封装
│       │   ├── data/                       # Preferences/RelationalStore
│       │   └── common/                     # 常量、工具、错误码
│       └── resources/
├── gecko/                                  # HSP：Native 模块
│   ├── build-profile.json5
│   ├── oh-package.json5
│   ├── hvigorfile.ts
│   └── src/main/
│       ├── module.json5                    # type: "shared"
│       ├── ets/                            # ArkTS facade（可选）
│       ├── cpp/                            # NAPI 桥接 + CMake
│       │   ├── CMakeLists.txt
│       │   ├── include/
│       │   └── src/
│       ├── libs/arm64-v8a/                 # Gecko/SpiderMonkey 预编译 .so
│       └── resources/
├── third_party/
│   └── gecko/                              # 上游源码与补丁
│       ├── source/                         # Firefox/Gecko checkout
│       ├── patches/                        # OHOS 适配补丁
│       ├── mozconfig/                      # 构建配置
│       └── scripts/                        # 同步/构建辅助脚本
├── build/
│   └── gecko/                              # out-of-tree 构建产物
│       ├── obj-aarch64-ohos/
│       └── artifacts/                      # 暂存 .so、头文件、清单
├── scripts/                                # 工程级构建/校验/部署脚本
└── spec/                                   # 规格、计划、任务
```

**Structure Decision**: 保留现有 Stage 模型与 `entryability/pages` 结构；浏览器 UI 属于 greenfield，采用 **MVVM + State Management V2**，按 `pages/views/components/viewmodel/model/service/data/common` 划分职责，目标 10-14 个 ArkTS 文件，避免为每个概念单独建文件。Native 引擎放入独立 `gecko` HSP，Gecko 源码放入 `third_party/gecko`，构建产物放入 `build/gecko`。该结构既满足浏览器 UI 的多页面/持久化/可测试性，也避免 DevEco 直接索引 Gecko 全量源码。

## Complexity Tracking

| 复杂度 | 为什么需要 | 更简单的替代方案为何不够 |
|---|---|---|
| 独立 `gecko` HSP | Gecko 体量大、原生依赖多，需要与 ArkTS UI 解耦；HSP 支持 C++ 库与资源共享 | 单 `entry` 模块会把引擎构建、UI 构建、签名耦合在一起，迭代与排障成本高 |
| `third_party/gecko` 独立源码树 | 上游使用 `mach`/`mozbuild`，需要 out-of-tree 构建与补丁管理 | 放进 `entry/src/main/cpp` 会被 DevEco 索引，构建边界不可控 |
| 解释器优先的 JIT 策略 | 第三方引擎 JIT 受限，ACL 审批不确定；坚盾模式可全局禁用 JIT | ACL 优先会把项目卡在审批上；纯解释器性能需通过架构优化弥补 |
| 单进程优先的进程模型 | 普通应用禁止 fork/exec，e10s 沙箱模型不可照搬 | 直接复刻 e10s 不可行；`ChildProcess` 仅支持无 UI 子进程，需后置 |

### Validation

- 计划遵循现有 `firefoxport` 的 Stage 模型与 `entryability/pages` 结构；仅因浏览器 UI 为 greenfield 而引入 MVVM + V2 目录。
- `gecko` HSP 与 `third_party/gecko` 的边界避免 DevEco 直接索引 Gecko 全量源码。
- 数据模型按 profile 隔离，避免私有模式数据泄漏。
- 接口契约以 NAPI 为唯一边界，ArkTS 不直接依赖 Gecko 内部类型。
- 所有 Native 产物通过 HAP/HSP 内嵌 `.so` 加载，符合本机 EPERM 约束。
- 每个里程碑都有可验证门禁与停止条件，避免无边界投入。

## Research & Decisions

### D1. 集成外壳

- **Decision**: 复用现有 `firefoxport` 工程作为 HAP 外壳与集成仓库。
- **Rationale**: 项目已配置 API 26、tablet/2in1、签名与 Stage 模型，避免重复搭建；UI 与引擎边界清晰。
- **Alternatives considered**: 新建独立工程（重复配置、签名/包名迁移成本）；纯命令行工程（缺少 DevEco 调试与签名链路）。

### D2. Gecko 源码与构建位置

- **Decision**: 源码位于 `third_party/gecko/source`，构建目录位于 `build/gecko/obj-aarch64-ohos`，产物暂存于 `build/gecko/artifacts`。
- **Rationale**: 上游构建系统与 HarmonyOS 工程解耦；out-of-tree 构建可清理、可复现；避免 DevEco 索引海量文件。
- **Alternatives considered**: 放在 `entry/src/main/cpp`（构建耦合、索引爆炸）；项目外独立仓库（用户已选择项目内 `third_party/gecko`）。

### D3. `gecko` 模块形态

- **Decision**: `gecko` 作为 HSP（动态共享包），包含 NAPI 桥接、C++ 嵌入层、预编译 `.so` 与资源。
- **Rationale**: HSP 支持 C++ 库与资源共享，跟随宿主应用、同进程、同生命周期；适合大体积引擎与后续多 HAP 复用。
- **Alternatives considered**: HAR（静态共享包，接入更简单，但原生库可能重复打包、体积膨胀）；单 `entry` 模块（耦合高）。若 Phase 0 发现 HSP 原生库打包受限，降级为 HAR 并将该决策记录在 M0 门禁。

### D4. 工具链

- **Decision**: Phase 0 以本机原生 aarch64-ohos 工具链为主：SDK clang 15.0.4 用于兼容性基线，Homebrew clang 22.1.8 + LLD 22.1.8 用于较新 Gecko；Rust 1.99.1（host `aarch64-unknown-linux-ohos`）；CMake 3.28.2、Ninja 1.13.2、Python 3.12.10。外部 Linux 构建机作为全量构建与 CI 备选。
- **Rationale**: 已验证 Rust 可生成 aarch64-ohos 可执行文件与 cdylib，clang 22 可编译并链接 OHOS 目标；本机迭代快。
- **Alternatives considered**: 仅外部 Linux 交叉编译（迭代慢、环境搭建成本高）；仅 clang 15（限制较新 Gecko 基线）。

### D5. Firefox 基线

- **Decision**: 以**项目启动时的最新 ESR** 为主基线；M0 先尝试构建最新 ESR，若 4 周内无法打通，回退 ESR 115 做 bring-up，产品阶段再回到最新 ESR。具体 ESR 版本在 M0 门禁锁定。
- **Rationale**: 最新 ESR 获得最长安全支持与现代 Web 能力，并与已验证的 clang 22 + Rust 1.99 匹配；ESR 115 仅作为早期构建回退，避免旧基线拖住整体进度。
- **Alternatives considered**: 固定 ESR 115（安全支持已结束、后续仍需升级）；mozilla-central（变化快、补丁维护成本高）。

### D6. JIT 策略

- **Decision**: M1 默认解释器模式；M1 完成后并行申请 `ohos.permission.kernel.ALLOW_EXECUTABLE_FORT_MEMORY` ACL，获批后以“解释器默认 + ACL 检测启用”的混合模式运行；坚盾模式下强制解释器。
- **Rationale**: 第三方引擎 JIT 默认禁止；ACL 审批不确定；坚盾模式可全局禁用 JIT。解释器优先可保证可运行性。
- **Alternatives considered**: ACL 优先（审批风险高）；永久无 JIT（性能损失需通过引擎优化与缓存弥补）。

### D7. 进程模型

- **Decision**: M1-M5 保持单进程；架构预留进程抽象层，M6 再评估 `ChildProcess`（无 UI、IPC）内容隔离；不复刻 e10s 沙箱。
- **Rationale**: 普通应用禁止 fork/exec；`ChildProcess` 可提供受限多进程，但能力与 Gecko 原生模型差异大。
- **Alternatives considered**: 直接移植 e10s（不可行）；完全单进程（安全隔离弱，需应用层补偿）。

### D8. 图形与窗口

- **Decision**: `XComponent`（SURFACE 类型）+ EGL/GLES 作为首选渲染路径；M3 先保证静态页稳定显示，GLES 失败自动切 SWGL；Vulkan 不进首版，作为后续优化项。
- **Rationale**: XComponent 提供原生 Surface 与 EGL/GLES/Vulkan 能力；GLES 覆盖更广，SWGL 可降低驱动依赖风险。
- **Alternatives considered**: 仅 Vulkan（设备/驱动覆盖不确定）；仅软件渲染（性能不足）。

### D9. 浏览器 UI

- **Decision**: ArkTS + ArkUI 实现浏览器 chrome（地址栏、标签栏、书签/历史、下载、设置）；引擎内容通过 `XComponent` 呈现，不使用系统 `Web` 组件承载 Gecko。
- **Rationale**: 系统不提供第三方 WebView 内核接入位；自绘是唯一可行路径；ArkUI 适合平板/2in1 的多窗口与分屏。
- **Alternatives considered**: 用系统 `Web` 组件（不是 Gecko，违背目标）；纯 Native UI（开发效率低、系统集成差）。

### D10. 账号同步

- **Decision**: 首版采用本地账户 + 导入/导出；Firefox Sync 兼容作为独立里程碑 M7，优先复用 Mozilla `application-services` 的 Rust crates（`fxa-client`、`sync15`、`places`、`viaduct`），不自研协议。
- **Rationale**: 复用 Mozilla 成熟实现可降低协议、加密与 schema 兼容风险；本地账户保证首版可用。
- **Alternatives considered**: 首版直接兼容 Firefox Sync（风险高、周期长）；从零实现 Sync（不推荐）；只做本地账户、不做 Sync（不满足用户完整移植目标）。

### D11. 构建与产物管线

- **Decision**: `scripts/` 提供工具链校验、Gecko 构建、产物暂存、`.so` 拷贝、HAP/HSP 构建与设备安装的统一入口；产物清单使用 JSON 记录版本、哈希、ABI、依赖。
- **Rationale**: 可复现、可审计、可 CI 化；避免手工拷贝导致的 ABI/签名错误。
- **Alternatives considered**: 手工构建与拷贝（不可复现）；把 Gecko 构建塞进 hvigor（构建系统耦合）。

### D12. 签名与执行

- **Decision**: 所有 Native 代码以 HAP/HSP 内嵌 `.so` 形式加载与签名；不依赖独立二进制执行；如需独立工具，使用签名工具或系统允许路径。
- **Rationale**: 实测自定义可执行文件在 `/tmp`、家目录、临时目录执行均返回 EPERM；HAP 内嵌 `.so` 是受支持路径。
- **Alternatives considered**: 直接执行 `mach`/`rustc` 产物（受 EPERM 限制）；关闭安全策略（不可行）。

### D13. 上游维护

- **Decision**: 采用“上游 ESR + OHOS 补丁队列”的 fork 模式；补丁按子系统分类，配套 rebase 脚本与回归清单；不假设 Mozilla 上游合并。
- **Rationale**: 平台适配补丁难以全部上游化；fork 是可控兜底。
- **Alternatives considered**: 完全跟踪上游（OHOS 补丁无法落地）；完全冻结版本（安全更新缺失）。

### D14. 测试策略

- **Decision**: 分层测试：工具链校验、NAPI 冒烟、JS shell、静态页渲染、网络加载、UI 端到端、Gecko 测试子集、性能/内存/稳定性 soak。
- **Rationale**: 每层失败可定位到具体子系统；避免“能启动但不可用”的假阳性。
- **Alternatives considered**: 只做端到端 UI 测试（定位困难）；只做单元测试（无法覆盖平台集成）。

### D15. 资源与停止条件

- **Decision**: Phase 0 采用最小构建（SpiderMonkey/headless）控制 16GB/119GB 资源风险；全量 Gecko 构建放到外部 Linux CI。任一 Go/No-Go 门禁连续失败即停止或转向。
- **Rationale**: 本机资源不足以支撑全量浏览器构建的长期迭代；先验证关键路径。
- **Alternatives considered**: 直接全量构建（OOM/磁盘耗尽风险高）；无门禁推进（沉没成本不可控）。

### First-Release Scope

| 范围 | 功能 | 里程碑 |
|---|---|---|
| **首版必须** | 地址栏/导航、多标签、书签、历史、下载、设置、隐私模式 | M5 |
| **首版不做** | 扩展体系、DRM/EME、广告拦截、Firefox Sync、Vulkan、ChildProcess | M7+ |
| **同步** | 本地账户 + 导入/导出；M7 用 application-services 实现 Firefox Sync | M5/M7 |

### Architecture

#### 分层架构

```text
┌─────────────────────────────────────────────────────────────┐
│ entry (HAP)                                                 │
│  ArkTS + ArkUI：地址栏 / 标签页 / 书签 / 历史 / 下载 / 设置   │
│  ViewModel + Service + Data（Preferences / RelationalStore） │
└───────────────────────────┬─────────────────────────────────┘
                            │ ArkTS facade / NAPI
┌───────────────────────────▼─────────────────────────────────┐
│ gecko (HSP)                                                 │
│  ArkTS facade（可选） → NAPI bridge → Gecko embedding layer  │
│  CMake：libgecko_napi.so + 预编译 libxul/libmozjs/...        │
└───────────────────────────┬─────────────────────────────────┘
                            │ C++ / platform services
┌───────────────────────────▼─────────────────────────────────┐
│ HarmonyOS platform                                          │
│  XComponent + EGL/GLES/Vulkan · NAPI · ACE · AVPlayer       │
│  File/Preferences/RelationalStore · HUKS/Asset · ChildProcess│
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│ third_party/gecko + build/gecko                              │
│  Firefox/Gecko source · patches · mozconfig · out-of-tree    │
└─────────────────────────────────────────────────────────────┘
```

#### 线程与事件模型

- **ArkTS UI 线程**：页面渲染、用户输入、ViewModel 状态更新。
- **NAPI 桥接线程**：ArkTS 调用进入 Native；禁止在非 UI 线程直接持有 `napi_env`/`napi_value`。
- **Gecko 引擎线程**：Gecko 主线程/事件循环；通过线程安全函数向 ArkTS 回调。
- **渲染线程**：EGL 上下文与 GLES 绘制；与 XComponent Surface 生命周期绑定。
- **回调路径**：Gecko → NAPI thread-safe function → ArkTS observer → ViewModel → UI。

#### 构建与产物管线

```text
1. third_party/gecko/source  ← Firefox/Gecko 源码 + patches
2. mozconfig + mach build    → build/gecko/obj-aarch64-ohos
3. stage artifacts           → build/gecko/artifacts（.so + headers + manifest.json）
4. copy .so                  → gecko/src/main/libs/arm64-v8a
5. gecko CMake               → libgecko_napi.so（链接 NAPI/ACE/Gecko 预编译库）
6. hvigor build              → gecko.hsp + entry.hap
7. sign + install            → 设备验证
```

#### Gecko 子系统移植矩阵

| 子系统 | Gecko 组件 | HarmonyOS 适配方式 | 里程碑 | 主要风险 |
|---|---|---|---|---|
| 构建系统 | `mach`、`mozbuild`、`configure` | 增加 OHOS target、工具链探测、sysroot、Rust 目标 | M0 | 构建脚本改动大、交叉依赖多 |
| 运行时 | NSPR、XPCOM | 线程/文件/时间/内存/IPC 适配；OHOS libc | M0-M1 | 线程/进程语义差异 |
| JS 引擎 | SpiderMonkey | 解释器模式；可选 JIT ACL | M1 | 无 JIT 性能、Rust 绑定 |
| 图形 | WebRender、GLES、SWGL | XComponent Surface + EGL/GLES；SWGL 兜底 | M2-M3 | 驱动兼容、黑屏、合成时序 |
| 窗口/输入 | widget、事件循环 | ArkUI 窗口/输入/IME/剪贴板/无障碍适配 | M2-M3 | IME/无障碍缺口 |
| 网络 | Necko、NSS | OHOS socket、DNS、代理、证书库 | M3-M4 | TLS/证书/代理差异 |
| 进程/安全 | e10s、沙箱 | 单进程优先；ChildProcess 后置；应用沙箱 | M1-M4 | 隔离弱、崩溃影响大 |
| 存储 | profile、cookie、cache、IndexedDB | 应用沙箱目录、配额、清理 | M3-M4 | 路径/权限/配额 |
| 下载 | Download Manager | ArkTS 文件 API + 通知 | M4-M5 | 文件权限、断点续传 |
| 媒体 | WebAudio、AV 播放 | AVPlayer/AVCodec NAPI；WebRTC/EME 后置 | M5-M6 | 编解码/DRM 缺失 |
| UI | 浏览器 chrome | ArkTS + ArkUI；MVVM + V2 | M4-M5 | 平板/分屏/多窗口适配 |
| 同步 | Firefox Accounts/Sync | 独立客户端；本地账户先行 | M7 | 协议/加密/合规 |
| 上游维护 | patch queue | rebase 脚本 + 回归清单 + CI | M6-M7 | 补丁漂移、安全响应 |

### Milestones & Go/No-Go Gates

| 里程碑 | 目标 | 主要交付物 | 估算 | Go/No-Go 门禁 |
|---|---|---|---|---|
| **M0 工具链与 HAP 冒烟** | 打通 HAP + NAPI + Rust/C++ `.so`；锁定 Firefox 基线 | `gecko` HSP 骨架、NAPI 冒烟、Rust cdylib 接入、构建脚本、基线锁定记录 | 2-4 周 | G0：设备安装启动；ArkTS→NAPI→Rust 调用成功；无 EPERM/签名问题 |
| **M1 SpiderMonkey 最小构建** | 在 OHOS 上构建并调用 `libmozjs.so` | `libmozjs.so`、JS 求值 NAPI、解释器模式 | 4-8 周 | G1：JS 求值正确；内存 < 500MB；无 JIT 可运行 |
| **M2 Headless Gecko** | 最小 Gecko 嵌入，无 UI | 静态 HTML 加载、DOM 导出、崩溃处理 | 8-16 周 | G2：静态页加载成功；进程稳定 30 分钟 |
| **M3 屏幕渲染** | Gecko 渲染到 XComponent | WebRender/SWGL、EGL/GLES、输入事件 | 12-24 周 | G3：静态页可见；滚动/点击可用；无黑屏 |
| **M4 网络与基础浏览** | Necko + 地址栏 + 单标签 | HTTPS 加载、前进/后退、错误页 | 12-24 周 | G4：真实网页可浏览；证书/代理通过 |
| **M5 多标签与数据** | 多标签、书签、历史、下载、设置 | `entry` UI + `RelationalStore` + 下载管理 | 12-24 周 | G5：核心浏览器流程通过；数据持久化 |
| **M6 产品硬化** | 性能、安全、媒体、无障碍、上架 | 60fps/内存优化、崩溃恢复、隐私合规 | 6-12 个月 | G6：性能/稳定性/合规达标 |
| **M7 账号同步（可选）** | Firefox Sync 兼容（application-services） | Sync 客户端、密钥管理、冲突解决 | 3-6 个月 | G7：同步正确性/安全性通过 |

**停止条件**：

- G0 连续 3 次失败：HAP/Native 路径不可行，停止或改为纯 ArkWeb 方案。
- G1 超过 8 周仍无法构建 SpiderMonkey：OHOS 原生 Gecko 路径不可行，停止。
- G3 超过 24 周仍无法稳定渲染：图形路径不可行，转向软件渲染或 ArkWeb。
- JIT ACL 被拒且解释器性能低于可用阈值：产品降级或转向。
- 应用商店明确拒绝自绘内核浏览器：产品转向 ArkWeb 体验层。
- 资源消耗超过选定资源档位 150%：停止并重新立项。

### Resource Profiles

| 档位 | 角色构成 | 人数 | 周期 | 适用阶段 |
|---|---|---|---|---|
| **POC** | Gecko/C++ ×2、平台/NAPI ×1、构建/基础设施 ×1、QA ×0.5 | 3-5 | 6-12 个月 | M0-M2 |
| **小团队** | Gecko ×3、图形 ×2、网络 ×1、平台 ×2、构建 ×1、QA ×2、产品/UX ×1 | 8-12 | 18-24 个月 | M0-M5 |
| **产品团队** | 上述 + 安全、媒体、无障碍、发布、运维、Mozilla 协作 | 15-25 | 24-36 个月 | M0-M7 |

**人月量级**：POC 约 30-60 人月；小团队约 200-300 人月；产品团队约 500-900 人月。以上为量级估算，需在 M0 后校准。

### Risks & Mitigations

| # | 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|---|
| R1 | JIT ACL 被拒 / 坚盾模式禁用 JIT | 高 | 高 | 解释器优先；引擎热路径优化；ACL 单独申请 |
| R2 | 禁止 fork/exec 导致无法复刻 e10s/沙箱 | 高 | 高 | 单进程优先；ChildProcess 后置；应用层隔离 |
| R3 | 系统不提供第三方 WebView 内核接入位 | 确定 | 高 | 自绘引擎 + XComponent；早期确认商店政策 |
| R4 | Gecko 构建系统 OHOS 适配失败 | 中高 | 高 | M0 工具链 spike；补丁分阶段；外部 CI 复现 |
| R5 | GLES 驱动兼容/黑屏/合成时序 | 中高 | 高 | SWGL 兜底；XComponent 生命周期测试；多设备验证 |
| R6 | 16GB 内存 / 119GB 磁盘不足 | 中 | 中高 | 最小构建；外部 Linux CI；ccache/sccache；清理策略 |
| R7 | Rust 1.99 与 Gecko 基线不兼容 | 中 | 中 | 固定 Rust 版本；ESR 回退；补丁 |
| R8 | IME/无障碍/剪贴板集成缺失 | 中高 | 中高 | ArkUI 原生能力优先；分阶段验收；可访问性测试 |
| R9 | 媒体/DRM 不可用导致视频站点失败 | 高 | 中 | AVPlayer 集成；EME/DRM 明确不在首版 |
| R10 | 上游不接受补丁，fork 维护成本高 | 高 | 中高 | 补丁队列；rebase 自动化；安全响应 SLA |
| R11 | 应用商店审核/合规风险 | 中 | 高 | 早期政策沟通；隐私合规；降级 ArkWeb 方案 |
| R12 | 性能不达可用阈值 | 中高 | 高 | 渲染/内存/启动优化；设备分级；性能门禁 |
| R13 | `application-services` crates 在 OHOS 上构建/运行失败 | 中 | 中 | M7 单独 spike；先用本地账户；必要时降级为最小同步实现 |

### Traceability Matrix

| 需求 | 计划覆盖 | 里程碑 |
|---|---|---|
| FR-001 Firefox 基线 | D5、M0 | M0 |
| FR-002 构建/打包/签名 | D2、D4、D11、D12、产物契约 | M0 |
| FR-003 基础运行时 | 子系统矩阵、D7 | M1 |
| FR-004 JIT 策略 | D6、M1 | M1 |
| FR-005 图形/合成 | D8、M3 | M3 |
| FR-006 网络/TLS/DNS/代理 | 子系统矩阵、M4 | M4 |
| FR-007 进程/沙箱 | D7、M1-M4 | M1/M4 |
| FR-008 浏览器 UI | D9、Project Structure、M5 | M5 |
| FR-009 账号同步 | D10、M7 | M7 |
| FR-010 媒体/IME/无障碍/文件/权限 | 子系统矩阵、M6 | M6 |
| FR-011 里程碑/资源/门禁 | Milestones、Resource Profiles | 全程 |
| FR-012 风险 | Risks | 全程 |
| FR-013 上游维护 | D13、M6-M7 | M6/M7 |
| FR-014 不依赖 WebView 内核 | D9、D12 | M3 |
| FR-015 Phase 0 POC | M0-M2 | M0-M2 |
| FR-016 停止条件 | Milestones / 停止条件 | 全程 |
| FR-017 资源档位 | Resource Profiles | 全程 |
| FR-018 首版功能范围 | Data Model、M5 | M5 |

### Open Decisions

| 决策 | 当前选择 | 决策点 |
|---|---|---|
| Firefox 具体 ESR 版本 | 最新 ESR；ESR 115 仅作 bring-up 回退 | M0 构建验证后锁定版本号 |
| `gecko` 包形态 | HSP（默认）/ HAR（回退） | M0 原生库打包验证 |
| JIT ACL | M1 解释器；ACL 并行申请 | M1 性能实测后决定是否启用 |
| Firefox Sync 实现细节 | M7 复用 application-services；首版本地账户 | M7 独立 spike |
| 全量构建 | 本机最小构建 / 外部 Linux CI | M2 资源实测后 |

## Data Model

### 实体

| 实体 | 关键字段 | 说明 |
|---|---|---|
| `Profile` | id、name、isPrivate、engineProfilePath、createdAt | 浏览器 profile；私有 profile 不落历史 |
| `Tab` | id、profileId、engineSessionId、url、title、favicon、loadingState、historyIndex、isPrivate、createdAt | 标签页；`engineSessionId` 映射 Gecko session |
| `Bookmark` | id、profileId、parentId、url、title、order、createdAt、modifiedAt | 支持文件夹层级 |
| `HistoryEntry` | id、profileId、url、title、visitedAt、visitCount | 按 profile 隔离；私有模式不写入 |
| `Download` | id、profileId、url、fileName、mimeType、totalBytes、receivedBytes、state、localPath、createdAt | 下载状态机 |
| `Setting` | key、value、type、updatedAt、schemaVersion | 设置项；按 schema 版本迁移 |
| `PermissionGrant` | origin、permission、decision、updatedAt | 站点权限 |
| `SyncAccount` | accountId、email、deviceId、lastSyncAt、keyRef | 可选；密钥只在 HUKS/Asset 中引用 |
| `EngineSession` | sessionId、profileId、processMode、jitMode、surfaceId、state | Native 侧会话状态 |

### 状态转换

- **Tab**: `created → loading → loaded → (crashed | closed)`；`loading → stopped`；`loaded → loading`（导航）。
- **Download**: `queued → downloading → (paused | completed | failed | canceled)`；`paused → downloading`；`failed → queued`（重试）。
- **EngineSession**: `created → initializing → ready → rendering → suspended → destroyed`；`ready/rendering → crashed`。
- **Profile**: `created → active → archived/deleted`；删除时清理 engine profile 与用户数据。

### 存储映射

| 数据 | 存储 | 说明 |
|---|---|---|
| 设置 | Preferences | 轻量键值；schemaVersion 迁移 |
| 书签/历史/下载 | RelationalStore | 关系表 + 索引；按 profileId 分区 |
| 引擎 profile | 应用沙箱文件系统 | `filesDir/gecko-profile/<profileId>` |
| 密钥/令牌 | HUKS / Asset Store | 不落明文；`SyncAccount.keyRef` 仅引用 |
| 缓存 | 应用缓存目录 | 可清理；受配额约束 |

## Contracts & Interfaces

### 1. NAPI 模块契约（`gecko` HSP）

模块名：`gecko`；原生库：`libgecko_napi.so`。所有接口在 ArkTS 侧通过 facade 暴露，Native 侧不直接依赖 ArkTS 页面。

| 接口 | 输入 | 输出 | 约束 |
|---|---|---|---|
| `initialize` | `EngineConfig`（profilePath、jitMode、processMode、logLevel） | `Promise<void>` | 进程内只初始化一次；重复调用返回幂等结果 |
| `shutdown` | 无 | `Promise<void>` | 释放引擎、Surface、线程；不可在渲染中调用 |
| `createSession` | `SessionOptions`（profileId、isPrivate、viewport） | `sessionId` | 返回唯一 ID；失败抛错误码 |
| `destroySession` | `sessionId` | `void` | 幂等；释放引擎会话与 Surface 绑定 |
| `loadUrl` | `sessionId`、`url` | `void` | URL 需规范化；私有会话不写历史 |
| `goBack` / `goForward` / `reload` / `stop` | `sessionId` | `void` | 无历史时为空操作 |
| `attachSurface` | `sessionId`、`surfaceId`、`width`、`height`、`density` | `void` | Surface 必须来自 XComponent；尺寸变化需重配 EGL |
| `detachSurface` | `sessionId` | `void` | 释放 EGLSurface，不销毁引擎会话 |
| `resizeSurface` | `sessionId`、`width`、`height` | `void` | 重配 viewport 与交换链 |
| `dispatchTouch` / `dispatchKey` / `dispatchWheel` / `dispatchIme` | `sessionId`、事件对象 | `void` | 事件坐标需与 Surface 对齐 |
| `evaluateScript` | `sessionId`、`script`、`timeoutMs` | `Promise<string>` | 仅用于测试/调试；默认禁用生产构建 |
| `getSessionState` | `sessionId` | `SessionState` | 返回 URL、标题、加载状态、崩溃状态 |
| `setObserver` | `EngineObserver` | `void` | 回调通过线程安全函数回到 ArkTS 线程 |
| `getVersion` | 无 | `EngineVersion` | 返回 Gecko/构建/ABI 信息 |

**错误码**：`NOT_INITIALIZED`、`INVALID_SESSION`、`SURFACE_ERROR`、`ENGINE_CRASH`、`UNSUPPORTED`、`IO_ERROR`、`TIMEOUT`、`PERMISSION_DENIED`。

**线程规则**：所有 NAPI 入口在 ArkTS 线程调用；Native 回调通过 `napi_threadsafe_function` 回到 ArkTS 线程；`napi_env`/`napi_value` 不跨线程持有。

### 2. ArkTS facade 契约（`gecko` 模块或 `entry` service）

| 类型 | 职责 | 关键方法/事件 |
|---|---|---|
| `GeckoEngine` | 引擎生命周期、全局配置 | `initialize`、`shutdown`、`getVersion` |
| `GeckoSession` | 单标签会话 | `loadUrl`、`goBack`、`goForward`、`reload`、`stop`、`evaluateScript` |
| `GeckoView` | XComponent 与 Session 绑定 | `attach`、`detach`、`resize`、输入事件转发 |
| `EngineObserver` | 引擎事件 | `onTitleChange`、`onUrlChange`、`onLoadStart`、`onLoadEnd`、`onProgress`、`onCrash`、`onRenderReady` |

**状态同步**：`GeckoSession` 的 URL/标题/加载状态通过 `EngineObserver` 更新 ViewModel；UI 不直接轮询 Native。

### 3. XComponent Surface 契约

| 阶段 | 动作 | 约束 |
|---|---|---|
| 创建 | `XComponent` 以 SURFACE 类型挂载 | 记录 `surfaceId`、尺寸、DPI |
| 绑定 | `attachSurface` 创建 EGLDisplay/EGLContext/EGLSurface | 必须在渲染线程；失败返回 `SURFACE_ERROR` |
| 渲染 | Gecko 合成 → GLES 绘制 → `eglSwapBuffers` | 与 UI 刷新节奏协调；避免主线程阻塞 |
| 尺寸变化 | `resizeSurface` 重建 viewport/交换链 | 防抖；避免频繁重建 EGLSurface |
| 销毁 | `detachSurface` 释放 EGLSurface | 不销毁 EngineSession；可重新绑定 |

### 4. 构建与产物契约

| 产物 | 来源 | 去向 | 校验 |
|---|---|---|---|
| `libxul.so` / `libmozjs.so` / `libnss3.so` 等 | `build/gecko/obj-aarch64-ohos` | `build/gecko/artifacts` → `gecko/src/main/libs/arm64-v8a` | ABI=aarch64；哈希；依赖清单 |
| `libgecko_napi.so` | `gecko/src/main/cpp` CMake | `gecko` HSP | 导出 NAPI 符号；链接 `libace_napi.z.so` |
| `gecko.hsp` | hvigor | `entry` 依赖 | 签名；版本；设备安装 |
| `entry.hap` | hvigor | 设备 | 签名；安装；启动 |

**产物清单**：`build/gecko/artifacts/manifest.json` 记录 Gecko 版本、Firefox 基线、clang/Rust 版本、ABI、每个 `.so` 的 SHA-256、依赖关系、构建时间。

### 5. 数据与存储契约

- `Preferences` 键名使用 `browser.<domain>.<key>` 命名空间；写入前校验 schemaVersion。
- `RelationalStore` 表：`profiles`、`tabs`、`bookmarks`、`history`、`downloads`、`permissions`；外键按 `profileId` 隔离；删除 profile 级联清理。
- Gecko profile 路径：`filesDir/gecko-profile/<profileId>`；私有 profile 使用独立临时目录，退出清理。
- 密钥：`SyncAccount.keyRef` 仅指向 HUKS/Asset 条目；日志与导出不得包含明文。

### 6. 测试契约

| 层级 | 测试 | 通过标准 |
|---|---|---|
| L0 | 工具链校验 | clang/CMake/Ninja/Python/Rust/Git 版本满足；OHOS target 可用 |
| L1 | NAPI 冒烟 | ArkTS 调用 Native 返回预期值；无崩溃 |
| L2 | JS shell | SpiderMonkey 解释器执行脚本并返回结果；内存 < 500MB |
| L3 | 静态页渲染 | 静态 HTML 在 XComponent 显示；首帧 < 5s |
| L4 | 网络加载 | HTTPS 页面加载；证书校验；代理可用 |
| L5 | UI 端到端 | 地址栏/标签/书签/历史/下载核心流程通过 |
| L6 | 稳定性 | 30 分钟 soak 无崩溃；内存无持续增长 |
| L7 | 兼容性 | 平板/2in1 分辨率、DPI、分屏、旋转通过 |
