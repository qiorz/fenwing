# 决策包：Gecko for HarmonyOS 移植立项

**版本**: 1.0
**日期**: 2026-11-17
**面向**: 立项决策者（技术负责人 / 产品负责人 / 安全合规 / 财务）
**结论有效期**: 6 个月，或任一 Go/No-Go 门禁结论变化时立即失效

---

## 0. 一页结论

**建议：条件性 Go（Conditional Go）**，先批准 M0-M1 的最小验证预算，M1 门禁通过后再批准 M2 及以后。

| 判断项 | 结论 |
|---|---|
| 技术可行性 | **部分已验证**：HAP + NAPI + Rust `.so` 链路已在本机编译通过；Gecko 全量构建未验证 |
| 平台合规可行性 | **待审批**：JIT ACL、自绘内核浏览器上架政策均需书面答复 |
| 工作量量级 | POC 30-60 人月；小团队 200-300 人月；产品团队 500-900 人月 |
| 主要不确定性 | SpiderMonkey 构建（G1）、图形渲染（G3）、商店政策 |
| 建议首笔投入 | M0 + M1（4-6 个月，3-5 人，约 15-30 人月） |
| 何时停止 | G0 连续 3 次失败；G1 超 8 周；G3 超 24 周；商店明确拒绝自绘内核 |

**为什么不是直接 Go**：本机 Python 环境缺 C 扩展，`mach` 无法运行，M1 尚无可复现的构建结果；在没有 G1 证据前批准全量预算属于不可控投入。

**为什么不是 No-Go**：M0 已证明最关键的“HAP 内嵌 Native 库”路径可用（NDK clang 15 编译 `libgecko_napi.so` 成功，链接 `libace_napi.z.so` / `libhilog_ndk.z.so`），且平台明确不提供第三方 WebView 内核接入位，自绘是唯一能满足“完整 Firefox”目标的路径。

---

## 1. 目标与非目标

### 1.1 目标

1. 把 Firefox/Gecko 移植到 HarmonyOS API 26（aarch64，优先 MatePad Edge tablet）。
2. 交付可日常使用的 Firefox 浏览器：地址栏/导航、多标签、书签、历史、下载、设置、隐私模式。
3. 保持与上游 ESR 的可维护关系：补丁队列 + rebase 流程 + 安全响应 SLA。

### 1.2 非目标（本期明确不做）

- 扩展体系（WebExtensions）、DRM/EME、广告拦截、Firefox Sync（M7 之前）、Vulkan 后端、`ChildProcess` 多进程。
- 手机/PC 形态适配（M6 之后）。
- 系统 WebView 内核接入（平台不提供该能力，也不符合目标）。

### 1.3 首版范围

| 范围 | 功能 | 目标里程碑 |
|---|---|---|
| 首版必须 | 地址栏/导航、多标签、书签、历史、下载、设置、隐私模式 | M5 |
| 首版不做 | 扩展、DRM、广告拦截、Firefox Sync、Vulkan、ChildProcess | M7+ |
| 同步 | 本地账户 + 导入/导出 | M5 |
| 同步（后续） | Firefox Sync 兼容（复用 Mozilla application-services） | M7 |

---

## 2. 基线选择

| 项 | 决策 | 依据 |
|---|---|---|
| Firefox 基线 | **项目启动时的最新 ESR**，M0 构建验证后锁定具体版本号 | 最长安全支持窗口 + 与现代 clang 22 / Rust 1.99 匹配 |
| 回退基线 | ESR 115（仅 bring-up 用，不作为产品基线） | 安全支持已结束，只用于验证构建链本身 |
| 跟踪策略 | fork：上游 ESR + OHOS 补丁队列 | 不假设 Mozilla 接受 OHOS 补丁 |
| 构建位置 | 本机做最小构建（SpiderMonkey/headless）；全量构建放外部 Linux CI | 本机 16GB 内存 / 约 119GB 可用磁盘不足 |

**M0 必须产出**：`third_party/gecko/baseline.json` 记录 tag、commit、锁定日期、校验和。未锁定版本 → 视为 M0 未完成。

---

## 3. 架构边界（三层）

```text
entry (HAP)     ArkTS + ArkUI 浏览器 UI；MVVM；Preferences / RelationalStore
   │  ArkTS facade → NAPI
gecko (HSP)     NAPI 桥 + Gecko 嵌入层 + 预编译 .so（libxul/libmozjs/...）
   │  C++ / 平台服务
HarmonyOS       XComponent(SURFACE) + EGL/GLES · NAPI · ACE · 文件/权限
   │
third_party/gecko + build/gecko    上游源码 · 补丁 · mozconfig · out-of-tree 构建
```

关键决策：
1. `gecko` 用 **HSP**（`type: "shared"`），失败可降级 HAR（在 M0 门禁记录）。
2. Native 代码**只**以 HAP/HSP 内嵌 `.so` 运行（EPERM 约束）。
3. JIT 默认解释器；ACL 作为可选加速路径单独申请。
4. 进程模型 M1-M5 单进程；`ChildProcess` 后置到 M6。
5. 渲染：XComponent(SURFACE) + EGL/GLES 主路径，SWGL 兜底；Vulkan 不进首版。

---

## 4. 里程碑与 Go/No-Go 门禁

| 里程碑 | 目标 | 交付物 | 估算 | 门禁（全部满足才 Go） |
|---|---|---|---|---|
| **M0** 工具链与 HAP 冒烟 | HAP + NAPI + Rust/C++ `.so`；锁定基线 | `gecko` HSP、NAPI 冒烟、Rust cdylib、构建脚本、baseline.json | 2-4 周 | **G0**：设备安装启动；ArkTS→NAPI→Rust 调用成功；无 EPERM/签名问题 |
| **M1** SpiderMonkey 最小构建 | OHOS 上构建并调用 `libmozjs.so` | `libmozjs.so`、JS 求值 NAPI、解释器模式 | 4-8 周 | **G1**：JS 求值正确；内存 < 500MB；无 JIT 可运行 |
| **M2** Headless Gecko | 无 UI 的最小 Gecko 嵌入 | 静态 HTML 加载、DOM 导出、崩溃处理 | 8-16 周 | **G2**：静态页加载成功；进程稳定 30 分钟 |
| **M3** 屏幕渲染 | Gecko → XComponent | WebRender/SWGL、EGL/GLES、输入事件 | 12-24 周 | **G3**：静态页可见；滚动/点击可用；无黑屏 |
| **M4** 网络与基础浏览 | Necko + 地址栏 + 单标签 | HTTPS 加载、前进/后退、错误页 | 12-24 周 | **G4**：真实网页可浏览；证书/代理通过 |
| **M5** 多标签与数据 | 浏览器壳补齐 | 多标签/书签/历史/下载/设置 + RelationalStore | 12-24 周 | **G5**：核心流程通过；数据持久化 |
| **M6** 产品硬化 | 性能/安全/媒体/无障碍/上架 | 优化与合规材料 | 6-12 个月 | **G6**：性能/稳定性/合规达标 |
| **M7** 账号同步（可选） | Firefox Sync 兼容 | Sync 客户端、密钥管理、冲突解决 | 3-6 个月 | **G7**：同步正确性/安全性通过 |

门禁执行规则：
- 每个门禁由**非实现者**复核，证据必须可复现（脚本 + 日志 + 产物哈希）。
- 门禁未通过不得启动下一里程碑的**主要**开发，只能做阻塞项修复。
- 门禁结论写入 `spec/gecko-porting-program/m1-report.md`（M1）等对应报告，并更新本文件第 0 节。

---

## 5. 资源档位

| 档位 | 角色构成 | 人数 | 周期 | 人月量级 | 适用阶段 |
|---|---|---|---|---|---|
| **POC** | Gecko/C++ ×2、平台/NAPI ×1、构建/基础设施 ×1、QA ×0.5 | 3-5 | 6-12 个月 | 30-60 | M0-M2 |
| **小团队** | Gecko ×3、图形 ×2、网络 ×1、平台 ×2、构建 ×1、QA ×2、产品/UX ×1 | 8-12 | 18-24 个月 | 200-300 | M0-M5 |
| **产品团队** | 上述 + 安全、媒体、无障碍、发布、运维、Mozilla 协作 | 15-25 | 24-36 个月 | 500-900 | M0-M7 |

成本换算口径：以上为人月量级，不含设备、CI 算力、商店合规咨询与外部 Linux 构建机。M0 后需按实际速度校准（校准结果写回本表并注明日期）。

---

## 6. 停止条件（Stop / Pivot）

| 触发条件 | 判定 | 动作 |
|---|---|---|
| G0 连续 3 次失败 | HAP/Native 路径不可行 | 停止原生移植，评估纯 ArkWeb 体验层 |
| G1 超过 8 周仍无法构建 SpiderMonkey | OHOS 原生 Gecko 路径不可行 | 停止；或改做“外部 CI 构建 + 仅集成”的窄范围试验 |
| G3 超过 24 周仍无法稳定渲染 | 图形路径不可行 | 转向纯 SWGL，或评估 ArkWeb |
| JIT ACL 被拒且解释器性能低于可用阈值 | 体验不可接受 | 产品降级（简化站点能力）或转向 |
| 应用商店明确拒绝自绘内核浏览器 | 无法上架 | 产品转向 ArkWeb 体验层 |
| 资源消耗超过选定档位 150% | 投入失控 | 停止并重新立项 |
| 任一合规硬约束被判定“不可行” | 无法上架 | 立即停止，不等下一个门禁 |

**暂停条件**（不停止，但冻结新开发）：安全响应 SLA 连续 2 个周期未达标；补丁队列冲突率 > 30%。

---

## 7. 需要决策者现在批准的事项

| # | 事项 | 需要谁 | 期限 | 不批准的后果 |
|---|---|---|---|---|
| D-1 | 批准 M0-M1 预算（约 15-30 人月） | 预算/技术负责人 | 立项会当周 | 无法产出 G1 证据，项目停在文档阶段 |
| D-2 | 提交 JIT ACL 申请（`ohos.permission.kernel.ALLOW_EXECUTABLE_FORT_MEMORY`） | 安全/合规 | M1 期间 | 只能走纯解释器，性能风险 R1 无法收敛 |
| D-3 | 向应用市场书面确认自绘内核浏览器政策 | 产品/法务 | M2 前 | R3/R11 无法收敛，可能在 M6 才发现不可上架 |
| D-4 | 指定外部 Linux 构建机（≥32 核 / 64GB 内存 / 500GB SSD） | 基础设施 | M1 结束前 | 全量 Gecko 构建无法进行 |
| D-5 | 确认 Firefox 商标与品牌使用边界 | 法务 | M2 前 | 发布命名与图标方案不确定 |

---

## 8. 30 分钟评审议程（建议）

| 时间 | 议题 | 产出 |
|---|---|---|
| 0-5 min | 读第 0 节结论 | 是否接受“条件性 Go” |
| 5-12 min | 里程碑与门禁（第 4 节） | 确认 G0-G2 的通过标准无争议 |
| 12-18 min | 资源档位与首笔投入（第 5 节） | 选定档位，批准 M0-M1 预算 |
| 18-24 min | 风险与停止条件（risk-register.md） | 确认可接受的风险敞口 |
| 24-30 min | 第 7 节 D-1..D-5 | 形成 Go / Conditional Go / No-Go 决议并记录 |

**Go 判定**：D-1 批准且 D-2/D-3 有明确责任人与期限。
**No-Go 判定**：D-3 明确回答“自绘内核浏览器不可上架”，且不接受 ArkWeb 降级方案。

---

## 9. 证据索引

| 证据 | 位置 |
|---|---|
| 需求与验收场景 | `spec/gecko-porting-program/spec.md` |
| 技术路线与架构 | `spec/gecko-porting-program/plan.md` |
| 任务分解与依赖 | `spec/gecko-porting-program/tasks.md` |
| 风险登记册 | `spec/gecko-porting-program/risk-register.md` |
| 安全与合规结论 | `spec/gecko-porting-program/security-compliance.md` |
| M1 构建/求值报告 | `spec/gecko-porting-program/m1-report.md` |
| 工具链版本证据 | `scripts/toolchain-manifest.json` |
| 实施状态 | `spec/gecko-porting-program/implementation-notes.md` |
