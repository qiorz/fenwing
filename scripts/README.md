# 构建 / 验证脚本索引（P3 工程化）

> 约定：**当前源码即权威状态**，`archive/` 中的一次性 patch 脚本仅作历史记录，勿再重放。

## 日常流水线

```powershell
# 1. 构建（HSP + HAP），失败时打印 ArkTS 错误
powershell -File D:\ff-ohos\scripts\build-all.ps1

# 2. 校验快照（体积预算、.permission、omni 内容、ACL、CRLF）
powershell -File D:\ff-ohos\scripts\verify-snapshot.ps1

# 3. 安装到设备（改过 HSP 时加 -Reinstall 卸载重装）
powershell -File D:\ff-ohos\scripts\install-device.ps1 -Reinstall

# 4. 冒烟测试（首帧 / 页面加载 / 右键菜单 / 进程存活）
powershell -File D:\ff-ohos\scripts\smoke-test.ps1

# 5. 长稳压测（可选，N 轮启停+标签+导航+关标签）
powershell -File D:\ff-ohos\scripts\soak-test.ps1 -Cycles 8
```

## 权威脚本

| 脚本 | 用途 |
|---|---|
| `build-all.ps1` | 一键构建 HSP+HAP，输出体积与错误 |
| `verify-snapshot.ps1` | 静态快照校验（PASS/FAIL） |
| `install-device.ps1` | 推送+安装（`-Reinstall` 处理 HSP 变更） |
| `smoke-test.ps1` | 设备冒烟（PASS/FAIL） |
| `soak-test.ps1` | 长稳压测 + RSS 采样 + 崩溃取证 |
| `build-omni.sh` | 由 dist 重建 omni（默认 STORED） |
| `build-gecko-full.sh` / `build-mozjs.sh` / `stage-engine.sh` | 引擎/依赖构建与暂存 |
| `enable-jit-libs.sh` | 注入 `.permission`、切换 JIT 库 |

## 归档

`archive/`：历史的一次性 patch（p0/p1/p15/p2x）、诊断与解析脚本。源码已包含其最终效果，重放可能造成回退。

## CI（本地）

`ci/run-local.ps1`：build → verify → smoke，一条命令跑完；退出码非 0 即失败。
