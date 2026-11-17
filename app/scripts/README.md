# scripts/ 命令契约

本目录是 Gecko for HarmonyOS 移植工程的**唯一构建入口**。所有命令都从仓库根目录执行，输出路径固定，便于复现与 CI 化。

## 0. 前置条件

- `DEVECO_SDK_HOME` 指向 HarmonyOS SDK（默认 `/data/service/hnp/hmos-clt.org/hmos-clt_1.0.0/sdk`）。
- Homebrew 工具链位于 `$HOME/.harmonybrew`（clang 22 / lld 22 / rustc 1.99 / git）。
- 目标设备通过 `hdc` 可见（`hdc list targets`）。
- `python3` **不在 PATH 上**，且 SDK Python 的 `lib-dynload` 为空（见 `implementation-notes.md` 6.1）。
  交付脚本只依赖可用的标准库子集，但仍必须用 SDK 解释器运行：

  ```bash
  PY=$DEVECO_SDK_HOME/default/openharmony/native/llvm/python3/bin/python3
  $PY scripts/stage_gecko_artifacts.py --copy
  ```

  构建脚本内部也通过 `$PYTHON` 自动探测该路径；可用 `PYTHON=/path/to/python3` 覆盖。
- 工具链版本记录在 [`toolchain-manifest.json`](./toolchain-manifest.json)（任务 T001）。任一版本漂移都视为 L0 校验失败。

> **硬约束**：自定义可执行文件在可写目录直接运行会返回 `EPERM`。任何验收都不得依赖“独立二进制可执行”；Native 代码必须打包为 HAP/HSP 内嵌 `.so`。

## 1. 目录契约

| 路径 | 内容 | 是否入库 |
|---|---|---|
| `third_party/gecko/source/` | Firefox/Gecko 上游 checkout（由 `fetch_gecko.py` 创建） | 否 |
| `third_party/gecko/patches/` | OHOS 适配补丁队列 | 是 |
| `third_party/gecko/mozconfig/` | `mozconfig` 模板 | 是 |
| `build/gecko/obj-aarch64-ohos/` | out-of-tree 构建目录 | 否 |
| `build/gecko/artifacts/` | 暂存产物（`.so`、头文件、`manifest.json`、日志） | 仅 `.gitkeep` |
| `gecko/src/main/libs/arm64-v8a/` | 规范暂存位置（CMake 从这里链接） | 仅 `.gitkeep` |
| `gecko/libs/arm64-v8a/` | hvigor 打包位置（`ProcessLibs` 只扫描 `<module>/libs/<abi>`） | 仅 `.gitkeep` |
| `gecko/src/main/cpp/` | NAPI 桥接与 CMake | 是 |

## 2. 命令清单

### 2.1 `build_gecko.sh` — Gecko/SpiderMonkey 构建

```bash
scripts/build_gecko.sh [--target js|gecko] [--jobs N] [--clean]
```

- 读取 `third_party/gecko/mozconfig/ohos-aarch64.mozconfig`。
- 使用 `third_party/gecko/source/mach build`，对象目录固定为 `build/gecko/obj-aarch64-ohos`。
- 日志写入 `build/gecko/artifacts/<target>-build.log`。
- 失败时以非零码退出，日志保留；**不伪造产物**。

### 2.2 `fetch_gecko.py` — 源码拉取与补丁应用

```bash
scripts/fetch_gecko.py [--baseline ESR128] [--force]
```

- 解析 `--baseline` 到 `third_party/gecko/baseline.json` 锁定的 tag。
- 浅克隆到 `third_party/gecko/source`，随后按序 `git apply third_party/gecko/patches/*.patch`。
- 网络不可用时退出码 2，并给出明确的阻塞信息。

### 2.3 `build_rust_smoke.sh` — Rust cdylib 冒烟

```bash
scripts/build_rust_smoke.sh [--release]
```

- `cargo build --target aarch64-unknown-linux-ohos`（链接器 = SDK clang）。
- 产物 `libohos_smoke.so` 复制到 `gecko/src/main/libs/arm64-v8a/`。

### 2.4 `stage_gecko_artifacts.py` — 产物暂存

```bash
scripts/stage_gecko_artifacts.py [--from build/gecko/obj-aarch64-ohos] [--no-copy]
```

- 从构建树收集 `.so` 与 JS 头文件，复制到 `build/gecko/artifacts/`。
- 生成 `build/gecko/artifacts/manifest.json`：Firefox 基线、ABI、SHA-256、依赖、构建时间、工具链。
- `--copy` 时同步 `libmozjs.so` 与头文件到 `gecko/src/main/libs/arm64-v8a/`。
- 缺失产物时打印 `MISSING` 并保持退出码 0（降级路径），`--strict` 时退出码 1。

### 2.5 `verify_gecko_bundle.py` — 产物校验

```bash
scripts/verify_gecko_bundle.py [--libs gecko/src/main/libs/arm64-v8a] [--manifest build/gecko/artifacts/manifest.json]
```

- 校验 ABI（ELF `e_machine == AArch64`、`EI_CLASS == 64`）。
- 校验必需导出符号（`napi_register_module_v1`、`ohos_rust_add`）。
- 校验 `manifest.json` 中的 SHA-256 与实际文件一致。
- 输出 `PASS/FAIL` 表格；任一 FAIL 退出码 1。

### 2.6 `rebase_gecko.py` — 上游 rebase

```bash
scripts/rebase_gecko.py --to <tag|branch> [--dry-run]
```

- 在 `third_party/gecko/source` 中切换到新基线并重放补丁队列。
- 生成 `build/gecko/artifacts/rebase-report.md`：成功、冲突、需人工处理的补丁清单。

## 3. HarmonyOS 构建与部署

```bash
# 构建（HAP + HSP）——必须显式列出两个模块
devecocli build --modules gecko entry

# 仅安装已构建产物
devecocli run --skip-build
```

- 签名使用根 `build-profile.json5` 中已有的 `default` `signingConfig`；**不要**修改签名材料。
- `devecocli build`（不带 `--modules`）只构建 `entry:assembleHap`，不会产出 `gecko.hsp`，
  运行时会找不到 `libgecko_napi.so`。**始终使用 `--modules gecko entry`**。
- 产物：
  - `gecko/build/default/outputs/default/gecko-default-signed.hsp`
  - `entry/build/default/outputs/default/entry-default-signed.hap`
- **部署必须同时安装 HAP 与 HSP**：HAP 的 `module.json` 里有
  `"dependencies":[{"moduleName":"gecko"}]`，缺少 `gecko.hsp` 时会报模块找不到。
  `devecocli run --skip-build` 通常会一并安装；若失败，先单独安装 `gecko.hsp` 再装 HAP。
- 预编译 `.so` 必须同时存在于 `gecko/src/main/libs/<abi>`（CMake 链接）和
  `gecko/libs/<abi>`（hvigor 打包）；`build_rust_smoke.sh` 与 `stage_gecko_artifacts.py` 都会写两处。

## 4. 顺序契约（M0/M1）

```text
1. scripts/fetch_gecko.py            # 拉源码 + 补丁（网络可用时）
2. scripts/build_rust_smoke.sh       # Rust cdylib → gecko/src/main/libs/arm64-v8a
3. scripts/build_gecko.sh --target js# SpiderMonkey 最小构建（时间盒 30-60 分钟）
4. scripts/stage_gecko_artifacts.py  # 产物 → build/gecko/artifacts + HSP libs
5. scripts/verify_gecko_bundle.py    # ABI / 符号 / 哈希校验
6. devecocli build                   # hvigor 编译 libgecko_napi.so + HAP/HSP
7. devecocli run --skip-build        # 安装并启动
```

任何一步失败都必须记录到 `spec/gecko-porting-program/m1-report.md` 的“阻塞点”章节，并说明降级路径；不得跳过校验直接声称通过。

## 5. 禁止项

- 不把 Gecko 源码放进 `entry/src/main/cpp` 或 `gecko/src/main/cpp`。
- 不在未获 ACL 批准时声明 `ohos.permission.kernel.ALLOW_EXECUTABLE_FORT_MEMORY`。
- 不提交 `build/gecko/obj-aarch64-ohos/`、`third_party/gecko/source/` 或大体积 `.so`。
- 不依赖 `mach`/`rustc` 产物作为独立可执行文件运行（EPERM）。
