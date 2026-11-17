# Feature Specification: Gecko for HarmonyOS 完整移植工程

**Created**: 2026-11-17
**Status**: Approved
**Input**: 用户要求在本机（HUAWEI MatePad Edge，HarmonyOS API 26）完整移植 Firefox/Gecko，并给出计划。用户明确选择“完整 Gecko 移植”路径，并接受完整浏览器 Demo 需分阶段交付；本机已确认具备原生 aarch64-ohos 工具链，可用于 Phase 0 最小 POC。

## Overview

本规格定义一个长期、分阶段的工程：将 Firefox 的 Gecko 引擎及其浏览器能力完整移植到 HarmonyOS（API 26，aarch64），最终形成可日常使用的 Firefox 浏览器。

当前阶段的交付物是**可执行的移植方案、架构设计、里程碑、资源估算与 Go/No-Go 门禁**。本机已确认具备原生 aarch64-ohos 工具链（clang、CMake、Ninja、Python），Rust/Git 已通过 Homebrew 安装并验证；因此 **Phase 0 的最小 POC（HAP 内嵌 Native 库、SpiderMonkey 最小构建）在本机具备验证条件**。完整浏览器 Demo 仍需在平台与构建门禁通过后，作为后续里程碑交付。

### 为什么需要独立规格

- 这是平台级移植工程，不是单个应用功能。
- 涉及构建系统、运行时、图形、网络、进程、安全、媒体、UI 多条主线。
- 需要明确的阶段门禁，避免在不可行路径上持续投入。
- 平台与应用商店约束必须先于代码投入被验证。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 立项决策者审阅完整路线 (Priority: P1)

作为项目负责人，我需要看到分阶段路线、资源档位、周期量级与 Go/No-Go 门槛，以便决定是否立项。

**Why this priority**: 没有可信的路线与门禁，工程无法获得资源，也无法在失败时及时止损。

**Independent Test**: 审阅方案文档，确认每个阶段都有目标、交付物、验收标准、依赖与风险。

**Acceptance Scenarios**:

1. **Given** 方案文档，**When** 审阅，**Then** 能回答“做什么、谁来做、多久、成本量级、何时停止”。
2. **Given** 任一里程碑，**When** 检查，**Then** 存在可验证的通过/不通过标准。
3. **Given** 任一 Go/No-Go 门禁，**When** 未通过，**Then** 方案给出停止或转向的明确动作。

---

### User Story 2 - 平台工程师评估适配边界 (Priority: P1)

作为平台工程师，我需要明确 Gecko 各子系统在 HarmonyOS 上的适配边界与工作量。

**Why this priority**: 工作量评估决定团队规模、排期与技术路线。

**Independent Test**: 对每个子系统（构建、线程、图形、网络、进程、JIT、媒体、UI）给出适配方式、依赖、风险与估算。

**Acceptance Scenarios**:

1. **Given** 子系统清单，**When** 检查，**Then** 无遗漏，且每项都有适配策略与工作量量级。
2. **Given** 高风险项，**When** 检查，**Then** 有降级方案与决策门。
3. **Given** 任一平台服务（输入法、无障碍、文件选择、权限），**When** 检查，**Then** 明确适配范围与缺失影响。
4. **Given** 本机原生工具链，**When** 执行 Phase 0 验证，**Then** clang、CMake、Ninja、Python、Rust、Git 可用，且 HAP 内嵌 Native 库可加载运行。

---

### User Story 3 - 安全与合规评审 (Priority: P1)

作为安全/合规负责人，我需要看到 JIT、进程模型、沙箱、应用商店政策的合规路径。

**Why this priority**: 任一硬约束不满足，产品无法上架；合规结论必须前置。

**Independent Test**: 审阅合规章节，确认每条硬约束都有“可行/不可行/待审批”结论与替代方案。

**Acceptance Scenarios**:

1. **Given** JIT 约束，**When** 审阅，**Then** 明确解释器模式与 ACL 申请两条路径的代价与性能影响。
2. **Given** 进程约束，**When** 审阅，**Then** 明确单进程、受限多进程、沙箱降级三种方案。
3. **Given** 应用商店对自绘内核浏览器的政策，**When** 审阅，**Then** 明确上架路径与产品降级方案。

---

### User Story 4 - 产品负责人确认首版范围 (Priority: P2)

作为产品负责人，我需要确认首版浏览器功能范围与降级策略。

**Why this priority**: 首版范围决定用户体验、上市时间与资源分配。

**Independent Test**: 审阅功能范围表，确认基础浏览、多标签、书签/历史、下载、账号同步的优先级与降级方案。

**Acceptance Scenarios**:

1. **Given** 首版范围，**When** 审阅，**Then** 每项功能都有优先级、依赖与验收标准。
2. **Given** 账号同步，**When** 审阅，**Then** 明确 Firefox Sync 兼容与本地账户/导入导出两条路径。
3. **Given** 某功能无法在首版交付，**When** 审阅，**Then** 有明确的降级或延后策略。

---

### User Story 5 - 发布经理评估维护成本 (Priority: P3)

作为发布经理，我需要看到版本基线、上游 rebase、安全更新与长期维护策略。

**Why this priority**: 移植不是一次性项目，维护成本决定可持续性。

**Independent Test**: 审阅维护章节，确认版本策略、补丁管理、安全响应流程与回归范围。

**Acceptance Scenarios**:

1. **Given** Firefox 新版本发布，**When** 执行 rebase，**Then** 有明确流程与回归范围。
2. **Given** 安全漏洞，**When** 响应，**Then** 有 SLA 与补丁路径。
3. **Given** 上游不接受 OHOS 补丁，**When** 维护，**Then** 有长期 fork 的版本与补丁管理方案。

---

### Edge Cases

- 本机工具链版本不匹配（如 clang 版本过低）时，方案必须给出升级（Homebrew LLVM）或外部 Linux 构建的替代路径与停止条件。
- 本机对可写目录中的自定义可执行文件返回 EPERM 时，方案必须改用 HAP 内嵌 Native 库或完成二进制签名，不得假设独立二进制可直接运行。
- JIT ACL 审批被拒时，必须能退化为解释器模式，并给出性能影响与用户体验降级。
- 应用商店拒绝自绘内核浏览器时，必须给出产品降级方案（例如转向系统内核）。
- 图形驱动不支持目标 GLES/Vulkan 特性时，必须能退化为软件渲染。
- Firefox 上游不接受 OHOS 补丁时，必须给出长期 fork 维护方案。
- 目标设备内存不足导致多标签 OOM 时，必须给出标签休眠/丢弃策略。
- 设备系统升级导致原生接口行为变化时，必须有兼容性回归清单。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 方案 MUST 以 Firefox 官方源码为基线，明确版本选择策略（ESR 与 mozilla-central 的取舍）与升级节奏。
- **FR-002**: 方案 MUST 定义 HarmonyOS aarch64 的本机原生构建与外部 Linux 交叉编译两条路径，以及产物打包、签名与安装验证流程。
- **FR-003**: 方案 MUST 覆盖 Gecko 基础运行时（线程、文件、时间、内存、IPC）在 HarmonyOS 上的适配策略。
- **FR-004**: 方案 MUST 覆盖 JavaScript 引擎在 JIT 受限条件下的运行策略（解释器、ACL、混合模式）。
- **FR-005**: 方案 MUST 覆盖图形与合成后端（GPU 与软件渲染）与 HarmonyOS 原生表面的集成策略。
- **FR-006**: 方案 MUST 覆盖网络栈、TLS、DNS、代理、证书与下载的适配策略。
- **FR-007**: 方案 MUST 覆盖进程模型与沙箱策略，明确与 HarmonyOS 进程约束的兼容方式。
- **FR-008**: 方案 MUST 覆盖浏览器 UI 能力：地址栏、导航、多标签、书签、历史、下载、设置。
- **FR-009**: 方案 MUST 覆盖账号同步的两种路径评估：Firefox Sync 兼容与本地账户/导入导出。
- **FR-010**: 方案 MUST 覆盖媒体播放、输入法、无障碍、文件选择、权限等平台服务适配范围。
- **FR-011**: 方案 MUST 定义分阶段里程碑、依赖关系、资源档位、周期量级与 Go/No-Go 门禁。
- **FR-012**: 方案 MUST 定义不少于 10 项风险及缓解措施，覆盖平台政策、JIT、进程、图形、上游维护。
- **FR-013**: 方案 MUST 定义上游同步、安全更新、回归测试与长期维护策略。
- **FR-014**: 方案 MUST 明确不假设系统 WebView 内核接入位，采用应用内自绘/嵌入路径。
- **FR-015**: 方案 MUST 定义 Phase 0 最小 POC（HAP 内嵌 Native 库、SpiderMonkey 最小构建）的前置条件与验收标准。
- **FR-016**: 方案 MUST 定义“停止条件”，明确在哪些验证失败时终止或转向。
- **FR-017**: 方案 MUST 给出至少三种资源档位（POC、小团队、产品团队）的人月与周期量级。
- **FR-018**: 方案 MUST 明确首版功能范围与优先级，覆盖基础浏览、多标签、书签/历史、下载、账号同步。

### Key Entities *(include if feature involves data)*

- **移植阶段（Stage）**: 目标、范围、交付物、依赖、验收标准、Go/No-Go 门禁。
- **子系统适配项（Subsystem）**: 名称、现状、适配策略、工作量量级、风险、负责角色。
- **风险项（Risk）**: 类别、概率、影响、缓解措施、触发条件、决策门。
- **资源档位（Resource Profile）**: 角色构成、人数、周期、成本量级、适用阶段。
- **验收门禁（Gate）**: 指标、测试方法、通过阈值、失败后的动作。
- **功能范围项（Feature Scope）**: 功能名称、优先级、依赖、验收标准、降级策略。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 方案覆盖 Gecko 全部关键子系统，覆盖率 100%，无“待定”项。
- **SC-002**: 每个里程碑具备可验证的验收标准，任一标准可被第三方独立复核。
- **SC-003**: 给出至少 3 档资源方案（POC、小团队、产品团队），每档包含人数、周期与成本量级。
- **SC-004**: 识别不少于 10 项风险，每项有概率/影响评级与缓解措施。
- **SC-005**: 对 JIT、进程、商店合规三条硬约束给出明确结论（可行/不可行/待审批）与替代路径。
- **SC-006**: 方案可被工程团队直接拆解为 WBS，任务粒度不超过 2 周。
- **SC-007**: Phase 0 最小 POC 的前置条件清单完整，包含本机工具链版本、Rust/Git 验证、HAP 签名、源码获取、磁盘与内存余量。
- **SC-008**: 方案明确“停止条件”，避免无边界投入。

## Assumptions

- 本机（MatePad Edge，API 26，aarch64）可直接作为 Phase 0 构建环境：DevEco SDK 提供 clang 15.0.4、CMake 3.28.2、Ninja 1.13.2、Python 3.12.10；Homebrew 已安装 Rust 1.99.1（host aarch64-unknown-linux-ohos，含 std）、Git 2.56.1、LLVM 22.1.8 + LLD 22.1.8（keg-only）。
- 已验证：Rust 可生成 aarch64-ohos 可执行文件与 cdylib（导出符号正常），clang 22 可编译并链接 OHOS 目标；自定义可执行文件直接运行仍受 EPERM 限制，POC 必须走 HAP 内嵌 .so。
- 本机资源：16 核 CPU、16GB 内存、约 135GB 可用磁盘。全量 Gecko 构建可能不足，Phase 0 优先做最小构建；外部 Linux 构建作为全量与 CI 备选。
- 本机对可写目录中的自定义可执行文件存在 EPERM 限制；POC 必须以 HAP 内嵌 Native 库形式运行，独立二进制需签名或改用系统允许路径。
- HarmonyOS 集成工程复用现有 firefoxport 项目：Gecko 源码与构建树位于 third_party/gecko，工程模块划分为 entry（ArkTS UI/HAP）与 gecko（Native/NAPI）两个模块。
- 目标设备优先 MatePad Edge（tablet，API 26）；手机/PC 作为后续目标。
- Firefox 基线优先 ESR，具体版本在 Phase 0 决策。
- Mozilla 官方合作与上游接受 OHOS 补丁不作为前提；长期 fork 维护作为兜底。
- JIT 默认按解释器模式规划；ACL 申请作为可选加速路径。
- 进程模型默认单进程 + 受限多进程；完整沙箱作为后续增强。
- 账号同步首版可采用本地账户/导入导出；Firefox Sync 兼容作为独立里程碑。
- 完整浏览器 Demo 不在当前阶段交付；Phase 0 最小 POC 在本机验证，完整 Demo 需通过平台与构建门禁后另行排期。

## Open Questions

- 已由 `plan.md` D5 决策：Firefox 基线采用项目启动时的最新 ESR；M0 锁定具体版本，ESR 115 仅作为 bring-up 回退。
- 已由 `plan.md` D13 决策：不假设 Mozilla 官方合作或上游合并；采用“上游 ESR + OHOS 补丁队列”的 fork 维护模式。
- 已由 `plan.md` D10 决策：首版本地账户 + 导入/导出；M7 复用 Mozilla `application-services` 实现 Firefox Sync 兼容。
