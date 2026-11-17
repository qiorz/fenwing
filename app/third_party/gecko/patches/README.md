# OHOS 补丁队列

本目录保存让 Firefox/Gecko 能在 HarmonyOS（API 26 / aarch64）上构建与运行的全部补丁。
补丁由 `scripts/fetch_gecko.py` 按文件名顺序应用，由 `scripts/rebase_gecko.py` 在新基线上重放。

## 命名规范

```text
<四位序号>-<子系统>-<简述>.patch
```

| 示例 | 含义 |
|---|---|
| `0001-ohos-target.patch` | 构建系统：新增 aarch64-unknown-linux-ohos target |
| `0002-runtime-thread-names.patch` | 运行时：线程命名 / 调度适配 |
| `0003-gfx-xcomponent-surface.patch` | 图形：XComponent surface 接入 |
| `0004-net-necko-socket.patch` | 网络：Necko socket/DNS 适配 |

规则：
1. 序号连续、不重复；删除补丁时保留序号空洞，不重排已有补丁。
2. 一个补丁只做一件事；跨子系统的改动拆成多个补丁。
3. 补丁必须能用 `git apply --check` 通过当前基线。
4. 每个补丁在文件头注释里写明：目的、影响范围、上游状态（未提交/已提交/被拒）、负责人。

## 分类

| 类别 | 前缀 | 说明 | 目标上游 |
|---|---|---|---|
| 构建/目标 | `ohos-target` | configure、mozbuild、target triple、sysroot | 可上游化 |
| 运行时 | `runtime-` | NSPR/XPCOM 线程、文件、时间、内存 | 部分可上游化 |
| JS | `js-` | SpiderMonkey 解释器模式、无 JIT 适配 | 部分可上游化 |
| 图形 | `gfx-` | WebRender/SWGL、XComponent、EGL/GLES | 难上游化（平台特定） |
| 网络 | `net-` | Necko、NSS、DNS、代理、证书库 | 难上游化 |
| 平台服务 | `platform-` | IME、无障碍、剪贴板、文件选择、权限 | 难上游化 |
| 安全 | `security-` | 沙箱降级、进程模型、ACL 检测 | 平台特定 |

## 0001-ohos-target.patch（骨架）

当前仓库中的 `0001-ohos-target.patch` 是**占位文件**：它只有注释和待办清单，没有
`diff --git` 段。`scripts/fetch_gecko.py` 会把它标记为 `SKIPPED (placeholder)`，
不会让整条流水线失败。

当基线锁定（`third_party/gecko/baseline.json` 的 `tag` 非空）且源码可达后，按以下步骤把它变成真补丁：

1. 在 `third_party/gecko/source` 新建分支 `ohos/aarch64-bringup`；
2. 修改 `moz.configure` / `build/moz.configure/*` / `python/mozbuild/mozbuild/*`；
3. `git diff > third_party/gecko/patches/0001-ohos-target.patch`；
4. `git apply --check` 验证；
5. 在补丁头部补上"目的/影响/上游状态/负责人"。

## 上游状态标记

每个补丁头注释必须含一行 `Upstream: none | proposed | merged | rejected`，并附日期。
这决定 rebase 时的处理策略：`merged` 的补丁直接从队列删除，`rejected` 的进入长期 fork 维护清单。

## 禁止项

- 不要在补丁里包含构建产物、`.so`、测试数据大文件。
- 不要把多个不相关修复塞进同一个补丁。
- 不要修改 `third_party/gecko/source` 却不产出补丁（rebase 时会丢失）。

## 计划中的补丁队列（M0-M5）

| 序号 | 文件 | 子系统 | 目标里程碑 | 上游状态 |
|---|---|---|---|---|
| 0001 | `0001-ohos-target.patch` | 构建/目标 | M1 | none（骨架） |
| 0002 | `0002-runtime-ohos-libc.patch` | 运行时（NSPR/XPCOM） | M1-M2 | none |
| 0003 | `0003-js-interpreter-only.patch` | JS（禁用 JIT/wasm baseline） | M1 | none |
| 0004 | `0004-gfx-xcomponent-surface.patch` | 图形（XComponent + EGL） | M3 | none |
| 0005 | `0005-gfx-swgl-fallback.patch` | 图形（SWGL 兜底） | M3 | none |
| 0006 | `0006-net-necko-ohos-socket.patch` | 网络（socket/DNS） | M4 | none |
| 0007 | `0007-net-nss-certdb.patch` | 网络（证书库） | M4 | none |
| 0008 | `0008-platform-ime-clipboard.patch` | 平台服务（IME/剪贴板） | M3-M6 | none |
| 0009 | `0009-security-sandbox-downgrade.patch` | 安全（单进程适配） | M2-M4 | none |

> 上表是**计划**，不代表已存在对应文件。除 0001 外，其余补丁必须在对应里程碑实现时创建，
> 不允许为了"队列完整"而创建空文件。

## 补丁生命周期

```text
编写 → git apply --check → 应用 → 本地验证 → 提交补丁文件
   ↑                                              │
   └──── rebase 冲突 → 手工解决 → 重新生成 ←──────┘
```

| 阶段 | 检查项 |
|---|---|
| 提交前 | `git apply --check` 在当前基线通过；头部字段齐全 |
| rebase 时 | `scripts/rebase_gecko.py --dry-run` 无冲突（或冲突已登记） |
| 发布前 | 回归清单（见 `spec/gecko-porting-program/upstream-maintenance.md` §5） |
| 上游合并后 | 从队列删除，并在 rebase 报告中记录 |

## 相关脚本

| 脚本 | 作用 |
|---|---|
| `scripts/fetch_gecko.py` | 拉源码 + 按序应用补丁；占位补丁记 SKIPPED |
| `scripts/rebase_gecko.py` | 新基线上重放补丁，输出 `build/gecko/artifacts/rebase-report.md` |
| `scripts/build_gecko.sh` | 用 `mozconfig/ohos-aarch64.mozconfig` 执行 mach 构建 |

## 快速自检

```bash
# 列出补丁与其占位状态
for f in third_party/gecko/patches/*.patch; do
  if grep -q "diff --git" "$f"; then echo "REAL      $f"; else echo "PLACEHOLDER $f"; fi
done
```
