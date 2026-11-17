# M1 报告：M0 冒烟 + SpiderMonkey 最小构建尝试

**日期**: 2026-11-17
**目标设备**: HUAWEI MatePad Edge / HarmonyOS API 26 / aarch64（tablet）
**结论**:
- **G0（HAP + NAPI + Rust）**：**构建侧通过**；设备侧安装/调用留待 Phase 9（本阶段禁止部署）。
- **G1（SpiderMonkey）**：**未通过 / 环境阻塞**。未产出 `libmozjs.so`，`evaluateScript` 走 `UNSUPPORTED` 降级路径。

---

## 1. M0 结果（已完成部分）

### 1.1 工具链

| 工具 | 版本 | 结果 |
|---|---|---|
| SDK clang | 15.0.4 | PASS |
| Homebrew clang | 22.1.8 | PASS |
| LLD | 22.1.8 | PASS |
| CMake / Ninja | 3.28.2 / 1.13.2 | PASS |
| Rust / Cargo | 1.99.1（target `aarch64-unknown-linux-ohos`） | PASS |
| Git | 2.56.1 | PASS |
| Python | 3.12.10（stdlib 不完整） | **FAIL**（见 3.1） |

完整记录：`scripts/toolchain-manifest.json`。

### 1.2 NAPI 桥编译（NDK clang 15 + CMake）

命令（等价于 hvigor 的 native 构建）：

```text
cmake -G Ninja -DCMAKE_TOOLCHAIN_FILE=$DEVECO_SDK_HOME/default/openharmony/native/build/cmake/ohos.toolchain.cmake \
      -DOHOS_ARCH=arm64-v8a -B <tmp> -S gecko/src/main/cpp
ninja -C <tmp>
```

结果：

```text
-- gecko: libmozjs not staged - evaluateScript returns UNSUPPORTED
-- gecko: linking Rust smoke bridge .../gecko/src/main/libs/arm64-v8a/libohos_smoke.so
[1/2] Building CXX object CMakeFiles/gecko_napi.dir/src/gecko_module.cpp.o
[2/2] Linking CXX shared library libgecko_napi.so
```

- 无编译警告（`-Wall -Wextra -fno-exceptions -fno-rtti -fvisibility=hidden`）。
- DT_NEEDED 实测：`libace_napi.z.so`、`libhilog_ndk.z.so`、`libohos_smoke.so`、`libc++_shared.so`、`libc.so`。

### 1.3 Rust cdylib

```text
scripts/build_rust_smoke.sh --release
  Compiling ohos-smoke v0.1.0
  Finished `release` profile [optimized] target(s) in 4.08s
```

导出符号（`llvm-readelf --dyn-syms`）：

```text
ohos_rust_add                FUNC GLOBAL DEFAULT
ohos_rust_bridge_version     FUNC GLOBAL DEFAULT
ohos_rust_probe              FUNC GLOBAL DEFAULT
```

DT_NEEDED：仅 `libc.so`（无 libstdc++/libgcc 依赖）。

### 1.4 HarmonyOS 构建与打包（关键发现）

```text
devecocli build --modules gecko entry
  BUILD SUCCESSFUL in 9 s 360 ms
```

`gecko-default-signed.hsp` 内容（`unzip -l`）：

```text
libs/arm64-v8a/libc++_shared.so     1262696
libs/arm64-v8a/libgecko_napi.so       27552
libs/arm64-v8a/libohos_smoke.so      273248
```

**发现 1（阻塞级，已修复）**：`devecocli build` 不带 `--modules` 时只执行 `entry:assembleHap`，
不会执行 `gecko:assembleHsp`，最终 HAP 内既没有 HSP 也没有任何 `.so`，运行必然失败。
→ 所有构建/验证命令统一为 `devecocli build --modules gecko entry`，已写入 `scripts/README.md`。

**发现 2（阻塞级，已修复）**：hvigor 的 `ProcessLibs` 只从 `<module>/libs/<abi>` 收集预编译 `.so`，
不从 `gecko/src/main/libs/<abi>` 收集。只放后者时 HSP 里**没有** `libohos_smoke.so`。
→ 现在 `build_rust_smoke.sh` 与 `stage_gecko_artifacts.py` 同时写入两处：
- `gecko/src/main/libs/arm64-v8a`（CMake 链接用，plan.md 约定路径）
- `gecko/libs/arm64-v8a`（hvigor 打包用）

### 1.5 ArkTS 编译

- `entry` 与 `gecko` 的 `CompileArkTS` 均成功，无 ArkTS 警告（`pushUrl` 已加 try/catch）。

---

## 2. M1 结果：SpiderMonkey 最小构建

### 2.1 执行记录

| 步骤 | 命令 | 结果 |
|---|---|---|
| 拉取源码 | `python3 scripts/fetch_gecko.py` | `BLOCKED: no baseline tag`（设计如此：不允许猜测基线） |
| 构建 | `scripts/build_gecko.sh --target js` | `ERROR: third_party/gecko/source/mach not found`（exit 2） |
| 日志 | `build/gecko/artifacts/js-build.log` | 已保留完整输出 |
| 产物 | `build/gecko/obj-aarch64-ohos/` | 空 |
| `libmozjs.so` | — | **未产出** |

**时间盒**：本次尝试未消耗 30-60 分钟——阻塞点在进入 `mach` 之前就已确定（见 3.1），
继续重试没有意义。

### 2.2 evaluateScript 的降级行为（已实现并校验逻辑）

| 场景 | 行为 |
|---|---|
| `libmozjs.so` + `jsapi.h` 未暂存 | CMake 不编译 `mozjs_eval.cpp`，`evaluateScript` 返回 reject，`code=UNSUPPORTED`，message 指向本报告 |
| 两者已暂存 | CMake 定义 `GECKO_HAVE_MOZJS=1`，编译 `mozjs_eval.cpp`，`JS::Evaluate` 同步求值并返回字符串 |
| `getVersion().jsEngine` | `unavailable` / `libmozjs`（由 `IsMozjsAvailable()` 决定，不写死） |
| `isJsEngineAvailable()` | 同上 |

`mozjs_eval.cpp` 已写好但**从未被编译过**（无头文件）。G1 时必须按锁定的 ESR 头文件核对：
`JS_NewRuntime` 参数、`JS::Evaluate` 重载、`JS_EncodeStringToUTF8` 的 include 路径。

### 2.3 内存

未测量（无可运行的 JS 引擎）。G1 通过标准仍为：JS 求值往返正确、进程 RSS < 500MB、无 JIT 可运行。

---

## 3. 阻塞点（含命令与错误原文）

### 3.1 SDK Python 3.12.10 缺少 C 扩展 → `mach` 无法运行

```text
$ $DEVECO_SDK_HOME/default/openharmony/native/llvm/python3/bin/python3 -c "import struct"
ModuleNotFoundError: No module named '_struct'

$ ... -c "import hashlib; hashlib.sha256(b'a')"
AttributeError: module 'hashlib' has no attribute 'sha256'

$ ... -c "from pathlib import Path"
ModuleNotFoundError: No module named 'math'

$ ... -c "import subprocess"
ModuleNotFoundError: No module named '_posixsubprocess'
```

根因：`.../python3/lib/python3.12/lib-dynload/` 为空；启动即提示
`Could not find platform dependent libraries <exec_prefix>`。

影响：`mach`/`mozbuild` 全部依赖这些模块，**本机无法执行 Gecko 构建**。

已做的缓解：
- 交付脚本改为不依赖 `struct`/`subprocess`/`hashlib`/`pathlib`/`tempfile`：
  ELF 头用 `int.from_bytes`，SHA-256 优先 `openssl dgst -sha256`，否则纯 Python 实现
  （已用 FIPS 标准向量校验：`sha256("abc") = ba7816bf...15ad`、`sha256("") = e3b0c442...b855`）。
- `scripts/stage_gecko_artifacts.py`、`scripts/verify_gecko_bundle.py` 已实测可运行（空 bundle 时输出 SKIP/MISSING）。

绕行：
1. **外部 Linux 构建机**执行 `mach build --enable-project=js`（推荐，plan.md D15 已规划）；
2. 修复 SDK Python（需要 OHOS 版 C 扩展，当前不可得）；
3. 不采用 Node 重写 mach（mach 是 Python 程序）。

### 3.2 基线未锁定

`third_party/gecko/baseline.json` 的 `tag` 为空是**有意**的：M0 要求锁定"启动时的最新 ESR"，
而当前环境无法访问上游、也不允许猜测 tag。`fetch_gecko.py` 因此在无 `--tag` 时以 exit 2 退出。

解除方式：`scripts/fetch_gecko.py --repo <url> --tag <ESR tag>`，或先填写 `baseline.json`。

### 3.3 网络/仓库地址

按安全约束，脚本不内置任何仓库 URL；必须由操作者通过 `--repo` 或 `GECKO_REPO_URL` 提供。

---

## 4. G0 / G1 判定

### G0 — HAP + NAPI + Rust

| 验收项 | 结果 | 证据 |
|---|---|---|
| HAP/HSP 可构建 | **PASS** | `devecocli build --modules gecko entry` → BUILD SUCCESSFUL |
| HSP 内含 NAPI + Rust `.so` | **PASS** | `gecko-default-signed.hsp` 列出 3 个 `.so` |
| NAPI 导出契约 | **PASS** | `gecko_module.cpp` 注册 23 个方法 |
| Rust 符号可链接 | **PASS** | `libgecko_napi.so` DT_NEEDED `libohos_smoke.so`；Rust 导出 3 个符号 |
| 设备安装启动 | **PENDING** | 设备在线（`hdc list targets` → `127.0.0.1:38247`），但部署属于 Phase 9 |
| ArkTS→NAPI→Rust 实机返回 42 | **PENDING** | 同上；UI 已实现（`Index.ets` 探测 21+21） |

部署注意：HAP 的 `module.json` 已包含 `"dependencies":[{"moduleName":"gecko"}]`，
安装时必须**同时**安装 `gecko.hsp`，否则启动即报模块缺失。

**G0 结论：构建侧通过（PASS-with-pending-device）。** 需 Phase 9 补齐设备侧两项后才算完整 G0。

### G1 — SpiderMonkey

| 验收项 | 结果 |
|---|---|
| `libmozjs.so` 构建 | **FAIL（环境阻塞）** |
| JS 求值正确 | **BLOCKED** |
| 内存 < 500MB | **BLOCKED（未测量）** |
| 无 JIT 可运行 | **BLOCKED** |

**G1 结论：未通过。** 属于环境级阻塞（3.1），不是代码缺陷。
按 plan.md 停止条件，G1 的 8 周计时应从**外部构建机可用**之日起算，而不是从今天起算。

---

## 5. 下一步（按顺序）

1. 提供外部 Linux 构建机，或修复 SDK Python 的 `lib-dynload`。
2. 锁定 ESR tag：填写 `third_party/gecko/baseline.json`，运行 `fetch_gecko.py --repo <url>`。
3. `scripts/build_gecko.sh --target js` → `libmozjs.so` + `jsapi.h`。
4. `stage_gecko_artifacts.py --copy` → 两个 libs 目录 + `manifest.json` + headers。
5. `verify_gecko_bundle.py --strict` → ABI/符号/哈希全 PASS。
6. 重新 `devecocli build --modules gecko entry`（此时 CMake 会自动启用 `mozjs_eval.cpp`）。
7. Phase 9：安装、启动、跑 `Index.ets` 的 M0 探测与 `JsSmokePage.ets` 的 JS 求值，回填本报告 4 节与内存数据。

---

## 6. 证据清单

| 证据 | 路径 |
|---|---|
| 构建日志 | `build/gecko/artifacts/js-build.log` |
| 产物清单 | `build/gecko/artifacts/manifest.json`（当前 status=partial） |
| Toolchain | `scripts/toolchain-manifest.json` |
| HSP | `gecko/build/default/outputs/default/gecko-default-signed.hsp` |
| HAP | `entry/build/default/outputs/default/entry-default-signed.hap` |
| NAPI 契约 | `gecko/src/main/cpp/include/gecko_napi.h` |
| 实施状态 | `spec/gecko-porting-program/implementation-notes.md` |
