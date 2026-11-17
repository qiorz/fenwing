# Firefox → HarmonyOS：旧工程资料包分析与合并计划

- 资料包：`C:\Users\Lenovo\Documents\firefoxport.zip`（7.2 MB / 773 项，2026-11-17 导出）
- 解压留档：`D:\ff-ohos\refs\firefoxport`（原样，只读参考）
- 干净工作副本：`D:\ff-ohos\work\firefoxport`（去掉 build/.hvigor/oh_modules 等产物）
- 分析时间：2026-11-17 14:30

---

## 1. 这份资料包是什么（结论先行）

一个**已经走到 M0/M1 的 HarmonyOS 浏览器工程**，由 DevEco 工程 + 完整规格文档组成，不是空壳：

| 组成 | 内容 | 状态 |
|---|---|---|
| `entry/` HAP | ArkTS 浏览器壳：地址栏、标签栏、书签/历史/下载/设置/隐私模式、RelationalStore 数据库、MVVM、XComponent(SURFACE) 宿主、JS 冒烟页 | ✅ 代码完整，已随 HAP 构建成功 |
| `gecko/` HSP | NAPI 桥（**23 个方法的门面契约**，见 `gecko_napi.h`）+ Rust 冒烟 cdylib `libohos_smoke.so` + CMake（NDK clang 15） | ✅ 已打进 `gecko-default-signed.hsp`（3 个 .so） |
| `scripts/` | `build_gecko.sh`（mach 封装）、`fetch_gecko.py`、`stage_gecko_artifacts.py`、`verify_gecko_bundle.py`、`rebase_gecko.py`、命令契约 `README.md` | ✅ 可运行（受 SDK Python 缺陷限制） |
| `third_party/gecko/` | baseline.json（**未锁 tag**）、mozconfig（SpiderMonkey only）、补丁目录（`0001` 是**占位骨架，无 diff**） | ⚠️ 契约就绪，实际 Gecko 目标适配缺失 |
| `spec/gecko-porting-program/` | plan（34 KB）、tasks（58 项）、decision-package（人月/停止条件）、security-compliance（JIT/进程/商店）、risk-register、m1-report、performance-baseline、upstream-maintenance | ✅ 文档质量高，可直接沿用 |
| 构建产物 | `gecko-default-signed.hsp`、`entry-default-signed.hap`、`.hvigor` 构建日志 | ✅ 构建侧 PASS（2026-11-17 13:04/13:09） |

### 它的里程碑现状（摘自 `m1-report.md`）

- **M0（HAP+NAPI+Rust）**：构建侧 PASS。`devecocli build --modules gecko entry` 成功；HSP 内含 `libgecko_napi.so`/`libohos_smoke.so`/`libc++_shared.so`；23 个 NAPI 方法已注册；Rust 导出 3 个符号。
- **M0 设备侧**：**PENDING**（T032/T056-T058 未做，HAP/HSP 从未装到 MatePad Edge）。
- **M1（SpiderMonkey）**：**FAIL（环境阻塞）**。原因不是代码：他们是在**鸿蒙 PC 本机**构建的，SDK 自带 Python 3.12 的 `lib-dynload` 为空（`import struct/hashlib/subprocess` 全挂），`mach` 起不来；也没有外部 Linux 构建机。`libmozjs.so` 未产出，`evaluateScript` 走 `UNSUPPORTED` 降级。
- 他们的下一步原文：① 提供外部 Linux 构建机 → ② 锁定 ESR tag → ③ `build_gecko.sh --target js` → ④ stage/verify → ⑤ 重建 HAP → ⑥ 设备验证。

### 关键工程结论（已踩过的坑，必须保留）

1. `devecocli build` 不带 `--modules gecko entry` 时只构建 entry，HAP 里没有任何 `.so` → 必须显式双模块。
2. hvigor 只从 `<module>/libs/<abi>` 打包预编译 `.so`；`gecko/src/main/libs/<abi>` 只给 CMake 链接用 → **两处都要放**。
3. 设备禁止执行可写目录里的自定义二进制（EPERM）→ 一切 native 代码只能进 HAP/HSP；`mach` 也必须用 `python3 mach` 方式调用。
4. JIT ACL 未获批 → `module.json5` 不声明 `ohos.permission.kernel.ALLOW_EXECUTABLE_FORT_MEMORY`，默认解释器模式（见 `security-compliance.md`）。
5. `targetSdkVersion = 26.0.0`，`deviceTypes = tablet, 2in1`，bundleName = `com.example.firefoxport`（占位名，签名 profile 需按它申请）。

---

## 2. 我们这边已经有什么（正好补它的缺口）

| 资源 | 位置 | 对应旧工程的缺口 |
|---|---|---|
| **外部 Linux 构建机** | WSL2 Ubuntu 24.04（`D:\WSL\Ubuntu2404`） | 直接解决 m1-report §3.1 的唯一硬阻塞 |
| OHOS 7.0-Release **Linux** native SDK（API 26） | `/opt/ohos-sdk/native`（clang 15.0.4 + musl sysroot + cmake/ninja） | 他们的 SDK 是鸿蒙 PC 版，Python 坏 |
| Gecko 源码（pinned 5836a06… = Firefox 142.0a1） | `/home/dev/ff/gecko` | 他们 baseline.json 未锁，源码从未拉到 |
| **社区 OHOS 移植层全量补丁已应用** | 同上（1015 文件变更） | 他们的 `0001-ohos-target.patch` 是空骨架，**OHOS 目标适配一行没写** |
| **mach configure 已通过** | `D:\ff-ohos\logs\configure-passed.log` | 他们的 mozconfig 标注 NOT YET VALIDATED |
| Rust 1.100 + OHOS target、cbindgen、node | WSL | 齐备 |

> 一句话：**他们缺的“外部 Linux 构建机 + OHOS 目标 patch”，我们这边已经就位并被 configure 验证过了。**

---

## 3. 三方资产对账：谁补谁

| 能力 | 旧工程（zip） | 社区 ohos_gecko 移植仓 | 合并结论 |
|---|---|---|---|
| ArkTS 浏览器壳 / 数据层 | ✅ 有 | ❌ 公开视图没有宿主工程 | **用旧的** |
| HAP/HSP 打包 + NAPI 门面（23 方法） | ✅ 有 | ❌ 无宿主 | **用旧的**；但底层要接社区的 Gecko 桥 |
| Gecko 源码 & OHOS 目标构建 | ❌ 未开始 | ✅ pinned 142 + v271 补丁 + widget/openharmony + ports/ohos | **用社区的** |
| Widget/窗口/输入/WebRender→XComponent | ❌ 只有 SURFACE 占位 | ✅ `widget/openharmony` 51 文件 + `geckoview.cpp`(4484 行) + XComponent/EGL 通路 | **用社区的** |
| NAPI ABI | 自研 23 方法门面 | 自研 NAPI 模块（`libgeckoview.so`）+ `GeckoBridge_*` 78 个导出符号（`libxul.symbols`） | **需要适配层**（见 §4） |
| 构建/校验/签名脚本 | ✅ 有契约 | ⚠️ build/ 目录未公开 | **用旧的 + 我们补的 WSL 脚本** |
| 规格/决策/合规文档 | ✅ 完整 | 仅移植技术文档 | **用旧的** |

---

## 4. 架构合并的三个选项（需要拍板）

**选项 A：旧壳 + 适配层（推荐）**
保留旧工程的 ArkTS UI/数据层/NAPI 门面；把 `gecko_module.cpp` 的实现换成对社区移植层的薄适配：由 `libgeckoview.so`（社区 NAPI 模块）装配 `XRE_main`、暴露 `GeckoBridge_*`（libxul 显式导出的 78 个符号），旧门面的 `createSession/loadUrl/attachSurface/...` 方法转调这些符号。
- 优点：UI 与产品体验资产全保留；进度最快。
- 代价：要写一层 API 映射（约 1–2 周，取决于 23 方法覆盖度）；旧壳的 XComponent 需改成 `libraryname='geckoxcomp'` 并补隐藏输入法桥（社区契约要求）。

**选项 B：社区宿主路线**
放弃旧 NAPI 门面，直接按社区契约重写 ArkTS 宿主（XComponent+隐藏 TextInput+chrome 幽灵化）。UI 层另起炉灶，旧壳只当参考。
- 优点：与社区移植层零阻抗。
- 代价：UI 重写；进度慢 3–6 周。

**选项 C：先只验设备路径（小步）**
先用 M1 的 `libmozjs.so` 打通“HAP+HSP+签名+设备+JS 求值”，再决定 A/B。
- 优点：最快拿到第一个真机证据，提前暴露签名/安装/JIT/沙箱问题。
- 代价：SpiderMonkey 单独构建约 0.5–1 小时，属额外分支工作。

**建议顺序：C → A**（今天先做 C 的设备链路，同时后台跑全量 libxul；然后按 A 合并）。

---

## 5. 需要先拍板的 5 个决策

| # | 决策 | 建议 | 依据 |
|---|---|---|---|
| D1 | 基线用 ESR 还是 142 | **先用 142（社区补丁已验证）**；ESR 迁移作为独立里程碑 | 旧工程 baseline.json 未锁；社区移植层 pinned 142；换基线要重放 1100+ 文件 |
| D2 | 架构 A/B/C | **C→A** | 见 §4 |
| D3 | JIT/ACL | 首版**解释器模式**（不声明 ACL）；ACL 并行申请，获批后再开 JIT 检测开关 | 旧工程 `security-compliance.md` §1；社区移植层 tablet 路径期望 JIT，需确认 no-JIT 可启动（手机路径即 no-JIT） |
| D4 | 品牌/bundleName | 保持 `com.example.firefoxport` 做内部验证；对外分发前换品牌（Firefox 商标限制） | 旧工程 §3.4 + 社区移植仓 MPL 声明 |
| D5 | 签名方式 | 用本机 **HO-Kit** 为 `com.example.firefoxport` 申请调试 profile，替换 build-profile 里指向鸿蒙 PC 的 `/storage/...` 签名材料 | HandBrake 已验证 HO-Kit 可行；旧 profile 路径在本机不存在 |

---

## 6. 下一步任务清单（按可执行顺序）

### P0 —— 今天/明天（打通链路，产生真机证据）

1. **把工作副本改造成本机可构建**（`D:\ff-ohos\work\firefoxport`）
   - `local.properties` 指向 `C:\Program Files\Huawei\DevEco Studio\sdk`；
   - `build-profile.json5` 签名段换成 HO-Kit 为 `com.example.firefoxport` 申请的材料（HO-Kit 已登录，证书 2027-09 到期）；
   - 保留 targetSdk 26.0.0 / tablet+2in1。
   - 验收：`hvigorw assembleHsp assembleHap`（或 DevEco 构建）成功产出 signed HSP/HAP。
2. **WSL 里构建 SpiderMonkey（补齐他们的 G1）**
   - 新 objdir + `--enable-project=js --target=aarch64-unknown-linux-ohos --enable-shared-js --disable-jit --disable-jemalloc`，复用我们的 OHOS 目标补丁；
   - 产出 `libmozjs.so` + `jsapi.h` → 用他们的 `stage_gecko_artifacts.py --copy` 放进 `gecko/src/main/libs/arm64-v8a` 与 `gecko/libs/arm64-v8a`。
   - 验收：`verify_gecko_bundle.py` ABI/符号/哈希 PASS；`JsSmokePage` 在真机返回求值结果（解释器模式）。
3. **真机验证（他们欠的 G0 设备侧）**
   - 连 MatePad Edge（USB 或 `hdc tconn`）→ 装 HSP+HAP → `Index.ets` 显示 Rust 42 → `JsSmokePage` JS 求值。
   - 这是旧工程 `tasks.md` 的 T032/T056-T058，也是后续一切的门禁。
4. **后台全量 libxul 构建**（我们已 configure 通过）
   - `bash /mnt/d/ff-ohos/scripts/build-gecko.sh 8`（nice 10，1–3 h，20–40 GB）；
   - 产物 `libxul.so` + `libgeckoview.so` + 14 个运行时依赖库 + NDK 的 `libc++_shared.so`/`libohinputmethod.so`/`libtime_service_ndk.so`。
   - 验收：`llvm-readelf` 检查 AArch64、无未解析符号；体积记录。

### P1 —— 下一个里程碑（M2 headless / M3 首帧）

5. **适配层**（选项 A）：按 `ports/ohos/geckoview.h` + `libxul.symbols` 的 78 个 `GeckoBridge_*`，把旧门面 23 方法映射出真实实现；先把 `createSession/loadUrl/getSessionState` 接通，加载 `about:blank`/静态页并 dump DOM。
6. **Surface 接入**：旧 `GeckoSurface` 的 XComponent 改为 `libraryname='geckoxcomp'`（社区契约），补尺寸/输入/IME 桥（社区已有 `OHOSNativeWindowBridge`/`nsWindow`/`HiddenImeBridge` 设计可抄）。
7. **打包纪律**：`.permission` ELF 段注入、`libgeckoxcomp.so` 删 build-id、`nativeLib.strip:false`、64K 对齐修复（社区 `docs/pitfalls.md` 全部适用）。
8. **验收（M3）**：静态页可见、滚动/点击可用、无黑屏；崩溃日志从设备 Faultlogger 取。

### P2 —— 产品化（M4+）

9. Necko 网络（`INTERNET` 权限）、HTTPS/证书、多标签/书签历史下载接入真实引擎；
10. 性能基线（他们 `performance-baseline.md` 已有口径）、内存上限、后台标签回收；
11. 安全合规：ACL 申请、应用市场书面答复（自绘内核）、隐私清单；
12. 上游维护：把社区移植层补丁与本工程补丁统一成补丁队列，按 `upstream-maintenance.md` 跑 rebase。

---

## 7. 风险（合并后新增）

| 风险 | 说明 | 缓解 |
|---|---|---|
| 两套 NAPI 契约 | 旧门面（23 方法） vs 社区 NAPI（GeckoBridge_* 78 符号）语义不完全对应 | 先做 getVersion/loadUrl/attachSurface 三条主链，其余显式 `UNSUPPORTED` |
| JIT ACL | 社区移植层 tablet 路径期望 JIT；无 ACL 需强制 no-JIT | 首版 no-JIT；用 `AIRWEB_FORCE_NO_JIT`（社区代码已有）验证启动 |
| HSP 签名 | 旧签名材料在鸿蒙 PC 本机，Windows 不可用 | HO-Kit 重申请 profile；HAP 与 HSP 用同一 signingConfig |
| 基线漂移 | 142 非 ESR；ESR 迁移成本高 | 先 142 出证据，ESR 作为后续独立里程碑（决策包 D2/D5） |
| 设备不在线 | 当前 `hdc list targets` 为空 | 让用户连上 MatePad Edge 再跑 P0-3 |

---

## 8. 现在的文件位置

| 内容 | 路径 |
|---|---|
| 原始资料包（工作区留档） | `D:\dsh\homo移植\refs\firefoxport.zip` |
| 解压原样 | `D:\dsh\homo移植\refs\firefoxport`（junction → `D:\ff-ohos\refs\firefoxport`） |
| 干净工作副本 | `D:\ff-ohos\work\firefoxport` |
| 已 configure 的 Gecko | WSL `/home/dev/ff/gecko`（objdir 已建） |
| 全量构建脚本 | `D:\ff-ohos\scripts\build-gecko.sh` |
| configure 日志 | `D:\ff-ohos\logs\configure-passed.log` |
| 施工状态 | `D:\ff-ohos\logs\status.md` |
