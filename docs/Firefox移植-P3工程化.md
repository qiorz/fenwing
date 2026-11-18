# Firefox / Gecko for HarmonyOS —— P3 工程化

> 时间：2026-11-18 · 目标：把"手工一条条命令"变成可重复、可验证、可自动化的流水线

## 一、落地内容

### 1) 一键脚本（`D:\ff-ohos\scripts`）

| 脚本 | 作用 |
|---|---|
| `build-all.ps1` | 配置 DevEco 环境 → 构建 HSP+HAP → 打印体积；失败时自动提取 ArkTS 错误 |
| `install-device.ps1` | 推送并安装；`-Reinstall` 卸载重装（HSP 变更必须用） |
| `verify-snapshot.ps1` | 静态快照校验（见下） |
| `smoke-test.ps1` | 真机冒烟：首帧 / 页面加载 / 右键菜单 / 进程存活，输出 PASS/FAIL |
| `soak-test.ps1` | 长稳压测（启停、标签、切换、导航、关标签、RSS 采样、崩溃取证） |
| `build-omni.sh` / `stage-engine.sh` / `enable-jit-libs.sh` | 引擎资源/产物/JIT 库流水线 |

### 2) 快照校验（`verify-snapshot.ps1`）

自动检查并输出 PASS/FAIL：
- 产物存在 + **HSP 体积预算**（≤270MB，可参数化）；
- `libxul.so` 含 **`.permission` 段**（JIT ACL）；
- `omni.ja` 内含上下文菜单实现（`ohosOpenContextMenu`、`__opentab__`）且为 deflate 版（≤30MB）；
- `module.json5` 含两条 ACL 声明；
- 关键 ArkTS 源码无 CRLF。

### 3) 本地 CI（`ci/run-local.ps1`）

`build → verify → smoke` 一条命令，任一步失败即返回非 0。实测：

```
PASS  HSP size budget 250.2 MB <= 270 MB
PASS  libxul .permission section
PASS  omni geckoview.js context menu
PASS  ACL: writable code memory
...
PASS  first-composite 12:33:49
PASS  page loaded (title event)
PASS  context menu shown
PASS  process alive
SMOKE TEST: PASS
CI LOCAL: PASS
```

### 4) 脚本收敛

- 175 个历史一次性 patch/诊断脚本归档到 `scripts\archive\`；
- `scripts\README.md` 明确"**当前源码即权威状态**，archive 仅历史记录，勿重放"，
  避免误用早期 patch 回退功能（JIT 开关、菜单、下载等）。

## 二、价值

- 任何人克隆工作区后，可按 README 四步复现：构建 → 校验 → 安装 → 冒烟；
- 体积/ACL/资源内容有**硬性校验**，防止回退（例如误把 JIT `.permission` 丢掉、误把 omni 换回未压缩或丢失菜单补丁）；
- 冒烟与长稳脚本可作为后续改动的回归门禁。

## 三、后续（P3 进阶）

1. 把 CI 接到真实仓库（GitHub Actions/GitLab Runner），设备冒烟用 self-hosted OHOS 设备池；
2. 构建缓存与 WSL 引擎构建的增量产物管理（当前 libxul 重编成本高）；
3. 版本号/变更记录自动化（versionCode 与 changelog 绑定）；
4. 冒烟用例扩展（下载、文件选择、全屏、查找、缩放），与 P2 功能一一对应。
