# scripts/

这些是移植过程中真正用过的脚本，不是「整理过的示例」。它们对路径有强假设：
Windows 侧 `D:\ff-ohos\...`，WSL 侧 `/home/dev/ff/gecko`、`/opt/ohos-sdk/native`。
复现时请先按自己的目录改路径（或直接用 [engine/apply-port.sh](../engine/apply-port.sh) +
[engine/README.md](../engine/README.md) 里的流程）。

## 目录

| 目录 | 内容 |
|---|---|
| `build/` | 主线：内核/JS 编译、产物铺放、JIT 开关、签名、权限段检查 |
| `setup/` | 一次性环境：WSL 安装、SDK 导入、工具链自检 |
| `bench/` | 性能基准的注入与采集（JIT vs 解释器） |
| `probes/` | 113 个历史探针：`inspect-*`、`patch-*`、`try*`、`show-*`，用于当时定位问题，仅作记录 |

## 最常用的几个

| 脚本 | 作用 |
|---|---|
| `build/build-gecko-full.sh` | WSL 内全量 `./mach build -j8`，日志落 `/home/dev/ff/gecko-build.log` |
| `build/build-mozjs.sh` | 单独编 SpiderMonkey（`--disable-jit --enable-shared-js`） |
| `build/build-omni.sh` | 从 `dist/bin` 打 `omni.ja`（`zip -0`，5385 个文件） |
| `build/stage-engine.sh` | 把 `libxul`/`libgeckoview`/NSS 依赖/NDK stub 库铺进 HSP 的 `libs/` |
| `build/enable-jit-libs.sh` | 给 `libxul.so` 注入 `.permission` 段，替换为 JIT 版 |
| `build/patch-jit-on.py` / `patch-jit-off.py` | 运行时开关 JIT（改启动参数与探测逻辑） |
| `build/check-permission-section.sh` | 检查 `.permission` 段是否在 |
| `build/sign-firefoxport.ps1` | 用 AGC 离线材料签 HAP/HSP（`hap-sign-tool.jar`） |
| `build/mozconfig` | 交叉编译配置（API 26 / `aarch64-unknown-linux-ohos`） |
| `bench/ab-param-bench.py` | 参数化基准页注入与结果采集 |
| `setup/02-wsl-bootstrap.sh` | WSL 内装依赖、Rust、mozbuild |

## 服务端路径是怎么来的

```
Windows:  D:\ff-ohos\work\firefoxport     ← DevEco 工程
          D:\ff-ohos\artifacts             ← 可复用的 strip 产物
          D:\ff-ohos\scripts               ← 这些脚本
WSL:      /home/dev/ff/gecko               ← Gecko 源码 + objdir
          /opt/ohos-sdk/native             ← OpenHarmony native SDK
```

## 编码

仓库内脚本已统一为 UTF-8（无 BOM）。`probes/` 里的脚本保留原样，仅做编码归一，
不保证在别人的机器上能直接跑——它们是取证记录，不是 API。
