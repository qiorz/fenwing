# 实施记录：Gecko for HarmonyOS（M0 / M1 范围）

**最后更新**: 2026-11-17
**对应任务**: T001-T032（Setup / Foundational / US1 / US2）+ Polish 收尾
**状态**: M0 骨架已落地；M1 受环境阻塞（详见第 6 节）

---

## 1. 环境事实（已实测，不是假设）

| 项 | 值 | 备注 |
|---|---|---|
| 设备 | HUAWEI MatePad Edge，API 26，aarch64 | 目标是 tablet |
| SDK | `DEVECO_SDK_HOME=/data/service/hnp/hmos-clt.org/hmos-clt_1.0.0/sdk` | |
| NDK clang | 15.0.4 | `libgecko_napi.so` 用它编译通过 |
| Homebrew clang | 22.1.8（`~/.harmonybrew/opt/llvm@22`） | Gecko 构建主编译器 |
| LLD | 22.1.8 | |
| CMake / Ninja | 3.28.2 / 1.13.2 | |
| Rust | 1.99.1（host = aarch64-unknown-linux-ohos） | 可编 cdylib |
| Git | 2.56.1 | |
| Node | 26.10.0 | 可用，作为 Python 的对照工具 |
| Python | 3.12.10 **但 stdlib 不完整** | 见 6.1，`lib-dynload` 为空 |

### 1.1 两个必须记住的硬约束

1. **EPERM**：可写目录里的自定义可执行文件直接运行会返回 `EPERM`。因此：
   - 不把“独立二进制可执行”作为任何验收条件；
   - 所有 Native 代码必须以 HAP/HSP 内嵌 `.so` 加载；
   - `mach` 也要用解释器调用（`python3 mach build`），不能 `./mach`。
2. **JIT ACL 未获批**：`entry/src/main/module.json5` 与 `gecko/src/main/module.json5` 都**没有**声明
   `ohos.permission.kernel.ALLOW_EXECUTABLE_FORT_MEMORY`。M1 只按解释器模式评估。

---

## 2. 目录与模块边界

```text
entry/                        HAP：ArkTS 浏览器壳（MVVM 目录已建）
gecko/                        HSP：NAPI 桥 + 预编译 .so
  src/main/cpp/               CMake + NAPI（不放大体积源码）
  src/main/libs/arm64-v8a/    stage 脚本投放 libohos_smoke.so / libmozjs.so
third_party/gecko/            上游源码 / 补丁 / mozconfig（不入 DevEco 索引）
build/gecko/                  obj-aarch64-ohos + artifacts（manifest、日志）
scripts/                      构建 / 暂存 / 校验 / rebase 的统一入口
```

规则：Gecko 源码**只**存在于 `third_party/gecko/source`，绝不放进 `entry/src/main/cpp`。

---

## 3. 构建顺序（可复现）

```bash
export DEVECO_SDK_HOME=/data/service/hnp/hmos-clt.org/hmos-clt_1.0.0/sdk
PY=$DEVECO_SDK_HOME/default/openharmony/native/llvm/python3/bin/python3

# 1) Rust cdylib（M0）
scripts/build_rust_smoke.sh --release
# 2) Gecko / SpiderMonkey（M1，时间盒 30-60 分钟）
scripts/build_gecko.sh --target js --jobs 16
# 3) 暂存产物 + manifest
$PY scripts/stage_gecko_artifacts.py --copy       # 缺产物时打印 MISSING，不伪造
# 4) 校验 ABI / 符号 / 哈希
$PY scripts/verify_gecko_bundle.py
# 5) HarmonyOS 构建（HAP + HSP）—— 必须显式列出两个模块
devecocli build --modules gecko entry
# 6) 安装并启动
devecocli run --skip-build
```

`scripts/README.md` 是命令契约的权威来源；本文件只记录实施状态。

---

## 4. NAPI 契约落地情况

| 接口 | 状态 | 说明 |
|---|---|---|
| `getVersion` | 已实现 | 返回 engine / geckoVersion / buildId / abi / jsEngine / initialized |
| `ping` | 已实现 | ArkTS → NAPI 往返，用于 M0 冒烟 |
| `initialize` / `shutdown` | 已实现（幂等） | 只初始化“桥”，不代表引擎已嵌入 |
| `createSession` / `destroySession` | 显式 `UNSUPPORTED` | M2 门禁后实现 |
| `loadUrl` / 前进后退 / stop | 显式 `UNSUPPORTED` | M2/M4 |
| `attachSurface` / `detachSurface` / `resizeSurface` | 显式 `UNSUPPORTED` | M3 |
| `dispatchTouch/Key/Wheel/Ime` | 显式 `UNSUPPORTED` | M3 |
| `getSessionState` / `setObserver` | 显式 `UNSUPPORTED` | M2 |
| `evaluateScript` | 降级路径已就绪 | `libmozjs.so` 缺失时以 `UNSUPPORTED` 拒绝 |
| `isJsEngineAvailable` | 已实现 | 反映 `libmozjs.so` 是否可用 |
| `rustAdd` | M0 冒烟 | ArkTS → NAPI → Rust |

错误码（C++ 与 ArkTS 两侧）：
`NOT_INITIALIZED`、`INVALID_SESSION`、`SURFACE_ERROR`、`ENGINE_CRASH`、`UNSUPPORTED`、`IO_ERROR`、`TIMEOUT`、`PERMISSION_DENIED`（ArkTS 侧额外有 `UNKNOWN` 兜底）。

线程规则：所有 NAPI 入口在 ArkTS 线程调用；M0/M1 不跨线程持有 `napi_env`/`napi_value`；M3 起回调用 `napi_threadsafe_function`。

---

## 5. 已落地文件

### Setup / Foundational
- `scripts/toolchain-manifest.json`
- `scripts/README.md`、`scripts/build_gecko.sh`
- `scripts/gecko_tooling.py`、`scripts/stage_gecko_artifacts.py`、`scripts/verify_gecko_bundle.py`
- `gecko/{build-profile.json5,oh-package.json5,hvigorfile.ts,obfuscation-rules.txt,Index.ets}`
- `gecko/src/main/module.json5`（`type: "shared"`）+ `resources/base/element/string.json`
- `gecko/src/main/cpp/CMakeLists.txt`、`include/gecko_napi.h`、`src/gecko_module.cpp`
- `gecko/src/main/cpp/types/libgecko_napi/{index.d.ts,oh-package.json5}`
- `gecko/src/main/ets/GeckoEngine.ets`
- `entry/src/main/ets/service/GeckoService.ets`
- `entry/src/main/ets/common/{GeckoTypes.ets,GeckoErrors.ets}`
- `entry/src/main/ets/components/GeckoSurface.ets`

### M0 / M1
- `gecko/rust/ohos-smoke/{Cargo.toml,src/lib.rs}`、`scripts/build_rust_smoke.sh`
- `scripts/fetch_gecko.py`、`third_party/gecko/mozconfig/ohos-aarch64.mozconfig`
- `third_party/gecko/patches/{README.md,0001-ohos-target.patch}`
- `third_party/gecko/baseline.json`（tag 待锁定）
- `entry/src/main/ets/pages/{Index.ets,JsSmokePage.ets}`
- `gecko/src/main/cpp/src/mozjs_eval.cpp`（仅在 libmozjs 暂存后编译）

### 浏览器壳 MVP（US4）
- `entry/src/main/ets/model/BrowserModels.ets`
- `entry/src/main/ets/data/{SettingsRepository.ets,BrowserDatabase.ets}`
- `entry/src/main/ets/viewmodel/TabViewModel.ets`
- `entry/src/main/ets/pages/BrowserPage.ets`（入口页）
- `entry/src/main/ets/components/{AddressBar.ets,TabBar.ets,GeckoSurface.ets}`
- `entry/src/main/ets/views/{BookmarksView.ets,HistoryView.ets,DownloadsView.ets,SettingsView.ets}`
- `entry/src/main/ets/service/LocalAccountService.ets`

### 文档
- `spec/gecko-porting-program/{decision-package.md,risk-register.md,security-compliance.md,m1-report.md}`
- `spec/gecko-porting-program/{implementation-notes.md,performance-baseline.md,upstream-maintenance.md}`

---

## 6. 已知阻塞与降级

### 6.1 SDK Python 3.12.10 缺少 C 扩展（阻塞 `mach`）

实测：

```text
$ python3 -c "import struct"
ModuleNotFoundError: No module named '_struct'
$ python3 -c "import hashlib; hashlib.sha256(b'a')"
AttributeError: module 'hashlib' has no attribute 'sha256'
$ python3 -c "from pathlib import Path"
ModuleNotFoundError: No module named 'math'
```

原因：`$DEVECO_SDK_HOME/.../native/llvm/python3/lib/python3.12/lib-dynload` 为空，且启动时提示
`Could not find platform dependent libraries <exec_prefix>`。

影响：
- `mach` 无法运行 → **T027 SpiderMonkey 构建在本机不可执行**（属于 G1 的环境级阻塞，不是代码问题）。
- 交付脚本已改为不依赖 `struct`/`subprocess`/`hashlib`/`pathlib`/`tempfile`：ELF 头用 `int.from_bytes` 解析，SHA-256 优先调用 `openssl dgst -sha256`，缺失时退化为纯 Python 实现（已用标准向量校验）。

绕行方案（按优先级）：
1. 外部 Linux 构建机 / CI 执行 `mach build`（plan.md D15 已把全量构建放到外部 Linux）；
2. 修复 SDK Python 的 `lib-dynload`（需要可用的 OHOS 版 C 扩展 wheel，当前不可得）；
3. 用 Node 26 重写 `mach` 驱动不可行（mach 是 Python 程序）。

### 6.2 网络

若 `scripts/fetch_gecko.py` 无法访问 Mozilla 仓库，脚本以退出码 2 结束并保留空目录，**不创建假源码**。

### 6.3 构建/打包的两个坑（已修复，务必保留结论）

1. **`devecocli build` 只构建 entry**：不加 `--modules gecko entry` 时只执行 `entry:assembleHap`，
   不会生成 `gecko.hsp`，HAP 内也没有任何 `.so`，设备上必然加载失败。
2. **hvigor 只从 `<module>/libs/<abi>` 收集预编译 `.so`**：放在 `gecko/src/main/libs/<abi>`
   的库不会被打包。现在脚本同时写两处：
   - `gecko/src/main/libs/arm64-v8a`（CMake 链接，plan.md 约定路径）
   - `gecko/libs/arm64-v8a`（hvigor 打包）

修复后 `gecko-default-signed.hsp` 内容：

```text
libs/arm64-v8a/libc++_shared.so
libs/arm64-v8a/libgecko_napi.so
libs/arm64-v8a/libohos_smoke.so
```

### 6.4 其他
- 完整构建验证属于 Phase 9（`spec-verify`）；本阶段已做编译检查：
  `devecocli build --modules gecko entry` 成功，0 error（仅剩 "Function may throw exceptions" 类提示性 WARN）。

---

## 7. 门禁检查清单

### G0 — HAP + NAPI + Rust（M0）
- [x] `gecko` HSP 注册在根 `build-profile.json5`，`entry` 依赖 `gecko`
- [x] `libgecko_napi.so` 能用 NDK clang 15 编译、链接 `libace_napi.z.so` + `libhilog_ndk.z.so`
- [x] NAPI 导出 `getVersion` / `ping` / 生命周期与全部契约桩
- [x] Rust cdylib 构建、链接（DT_NEEDED `libohos_smoke.so`）并打入 HSP
- [x] `devecocli build --modules gecko entry` 成功（HAP + HSP + 3 个 `.so`）
- [ ] 设备安装启动 + ArkTS→NAPI→Rust 实机调用（T032，需要 Phase 9 部署）

### G1 — SpiderMonkey（M1）
- [ ] `libmozjs.so` 构建（阻塞于 6.1）
- [ ] JS 求值正确、内存 < 500MB、无 JIT 可运行（阻塞）
- [x] 降级路径：`evaluateScript` → `UNSUPPORTED`，UI 明确展示而非假装成功

---

## 8. 与 plan.md 的偏差

| 偏差 | 原因 | 影响 |
|---|---|---|
| UI 状态管理用 V1（`@Component`/`@State`/`@Prop`）而非 V2 | 避免 V1/V2 混用导致的构建风险；MVP 组件树较小 | 架构（MVVM、ViewModel 分层）不变；可在 M5 前平滑迁移 |
| 预编译库同时写 `gecko/src/main/libs` 与 `gecko/libs` | hvigor 只扫描后者，CMake 用前者 | 多一份副本（约 0.4MB），换构建可靠性 |
| 交付脚本增加 `scripts/gecko_tooling.py` | SDK Python 缺 C 扩展，需要共享的纯 Python ELF/SHA-256 辅助 | 无功能偏差，仅多一个脚本内聚文件 |
| `gecko/src/main/cpp/types/libgecko_napi/` | NAPI 需要 `.d.ts` 才能被 ArkTS 强类型引用 | DevEco 标准做法 |

---

## 9. 下一步

1. 修复或绕开 SDK Python（6.1），在外部 Linux 跑通 `mach build --enable-project=js`，拿到 `libmozjs.so` + `jsapi.h`。
2. 跑 `scripts/stage_gecko_artifacts.py --copy`、`verify_gecko_bundle.py`，再验证 `evaluateScript`。
3. Phase 9：`devecocli build` → `devecocli run --skip-build` → UI 验证（T056-T058）。
4. G1 通过后才进入 M2（Headless Gecko）；未通过则按停止条件评估转向。
