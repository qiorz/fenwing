# 上游维护策略：Gecko for HarmonyOS

**版本**: 1.0
**日期**: 2026-11-17
**适用对象**: 发布经理、构建负责人、安全响应负责人

---

## 1. 版本基线策略

| 项 | 规则 |
|---|---|
| 主基线 | 最新 **ESR**（M0 锁定具体 tag，记录在 `third_party/gecko/baseline.json`） |
| 回退基线 | ESR 115，仅用于构建链 bring-up，不用于产品发布 |
| 升级节奏 | 跟随 ESR 大版本（约 12 个月一次）；安全补丁按 ESR 小版本（约 4 周）评估 |
| 锁定内容 | tag、commit、锁定日期、锁定人、`libmozjs.so` 的 SHA-256 |
| 变更审批 | 基线变更需构建负责人 + 安全负责人共同确认，并附回归报告 |

**禁止**：直接跟踪 mozilla-central（变更快、补丁维护成本不可控），或在未跑回归清单的情况下更新基线。

---

## 2. 补丁队列管理

### 2.1 分类

| 类别 | 前缀 | 上游可能性 | rebase 策略 |
|---|---|---|---|
| 构建/目标 | `ohos-target` | 中 | 优先尝试上游化；冲突时重写 |
| 运行时 | `runtime-` | 中 | 尽量小改动，便于重放 |
| JS | `js-` | 中低 | 与 JIT/解释器策略绑定，单独评审 |
| 图形 | `gfx-` | 低 | 平台特定，接受长期 fork |
| 网络 | `net-` | 低 | 平台特定，接受长期 fork |
| 平台服务 | `platform-` | 低 | 平台特定 |
| 安全 | `security-` | 低 | 每个补丁必须有威胁模型说明 |

### 2.2 补丁头部必填字段

```text
# Purpose : ...
# Scope   : ...
# Upstream: none | proposed | merged | rejected
# Owner   : ...
# Since   : <ESR tag>
```

`Upstream: merged` 的补丁在下次 rebase 时**必须删除**；`rejected` 的进入长期 fork 清单。

### 2.3 rebase 流程

```bash
# 1) 评估冲突面（不改工作树）
python3 scripts/rebase_gecko.py --to <new-esr-tag> --dry-run

# 2) 正式重放
python3 scripts/rebase_gecko.py --to <new-esr-tag> --repo <url> --keep-going

# 3) 查看报告
cat build/gecko/artifacts/rebase-report.md
```

报告状态含义：

| status | 含义 | 动作 |
|---|---|---|
| `clean` | 所有非占位补丁可应用 | 更新 `baseline.json`，跑回归清单 |
| `conflicts` | 至少一个补丁冲突 | 逐个手工解决并重新生成补丁 |
| `blocked` | 源码树/fetch/checkout 失败 | 先修环境 |

### 2.4 冲突处理原则

1. **先判断补丁是否还需要**：上游已合并 → 删除；平台已支持 → 删除。
2. **不要为了通过编译而放宽补丁**：冲突往往说明上游语义变了，需重新评估。
3. 每个解决后的补丁都要更新 `Since` 字段和头部说明。
4. 冲突率 > 30% 触发风险登记册 R10 的暂停条件。

---

## 3. CI 与构建

| 阶段 | 内容 | 频率 |
|---|---|---|
| L0 工具链 | `scripts/toolchain-manifest.json` 版本校验 | 每次构建 |
| L1 NAPI 冒烟 | `devecocli build --modules gecko entry` + `verify_gecko_bundle.py` | 每次提交 |
| L2 JS shell | `libmozjs.so` 构建 + `evaluateScript` 基准 | 每次 Gecko 变更 |
| L3 渲染 | 静态页首帧 | 每日 |
| L4 网络 | HTTPS/证书/代理 | 每日 |
| L5 UI E2E | 地址栏/标签/书签/历史/下载 | 每日 |
| L6 稳定性 | 30 分钟 soak | 每周 |
| L7 兼容性 | 平板/2in1、DPI、分屏、旋转 | 每个里程碑 |

**构建机要求**：Linux x86_64 或 aarch64，≥32 核 / 64GB 内存 / 500GB SSD；本机只做 NAPI/HSP 与最小验证。

产物入库规则：
- `.so` 必须带 `manifest.json`（SHA-256、ABI、工具链版本、构建时间）。
- 未通过 `verify_gecko_bundle.py` 的产物不得进入 `gecko/libs/<abi>`。
- CI 产物与本地产物哈希不一致时，以 CI 为准并排查环境差异。

---

## 4. 安全响应 SLA

| 严重级别 | 定义 | 响应时限 | 修复时限 |
|---|---|---|---|
| **Critical** | 远程代码执行 / 沙箱逃逸 / 在野利用 | 24 小时内确认 | 7 天内发版 |
| **High** | 可远程触发的内存破坏 / 信息泄露 | 3 个工作日 | 30 天内发版 |
| **Medium** | 需要用户交互的提权 / 数据泄露 | 10 个工作日 | 90 天内 |
| **Low** | 低影响缺陷 | 下个常规版本 | 无硬承诺 |

流程：
1. 订阅 Mozilla 安全公告（ESR 对应版本）。
2. 评估是否影响 OHOS 目标（部分漏洞依赖平台特性）。
3. 在补丁队列中 cherry-pick 对应修复；必要时回移上游补丁。
4. 跑回归清单 → 发版 → 更新 `baseline.json` 的 `securityPatchLevel`（可选字段）。

**禁止**：以"等下一个 ESR"为由延迟 Critical 修复。

---

## 5. 回归清单（每次基线/补丁变更必跑）

- [ ] 工具链版本与 `toolchain-manifest.json` 一致
- [ ] `devecocli build --modules gecko entry` 成功
- [ ] HSP 内含 `libgecko_napi.so` / `libohos_smoke.so` / 预编译 Gecko 库
- [ ] `verify_gecko_bundle.py --strict` 全 PASS
- [ ] `getVersion()` 返回新的 `geckoVersion`
- [ ] `ping` 与 `rustAdd` 往返正确（M0 链路未回归）
- [ ] `evaluateScript('1+1')` 返回 `2`（M1 后）
- [ ] 静态页渲染（M3 后）
- [ ] HTTPS 加载与证书校验（M4 后）
- [ ] 书签/历史/下载持久化（M5 后）
- [ ] 隐私模式不写历史（每次）
- [ ] 30 分钟 soak 无崩溃、无持续内存增长（M2 后）
- [ ] 更新 `implementation-notes.md` 与 `m1-report.md` 对应章节

---

## 6. 角色与职责

| 角色 | 职责 |
|---|---|
| 发布经理 | 版本节奏、门禁组织、对外发布说明 |
| 构建负责人 | 工具链、CI、产物哈希、rebase 执行 |
| 安全负责人 | CVE 评估、SLA 跟踪、ACL 申请 |
| Gecko 负责人 | 补丁质量、上游化推进、冲突裁决 |
| QA | 回归清单执行、性能基线复测 |

---

## 7. 长期 fork 的维持成本控制

1. **补丁总量上限**：超过 60 个补丁或 15k 行时，强制做一次"合并/上游化"专项。
2. **每季度评估**：列出补丁的 `Upstream` 状态与维护成本，关闭无价值补丁。
3. **禁止补丁漂移**：所有修改必须落成补丁文件，禁止只改 `third_party/gecko/source`。
4. **文档同步**：补丁数量、冲突率、SLA 达成率写入季度报告。
