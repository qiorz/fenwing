# Firefox → HarmonyOS 7（API 26）移植：本机环境体检报告

- 体检时间：2026-11-17 12:18–12:35（Asia/Shanghai）
- 体检方式：**静默只读**。未安装任何软件、未改注册表/环境变量、未启动任何 GUI、未连接设备；hdc 服务临时启动一次后已 `kill`；唯一写入是本报告文件。
- 目标设备：HUAWEI MatePad Edge（`QXS-W00`，tablet，arm64-v8a，16 核 / 16 GB）：HarmonyOS 7.0.0.109 / **API 26** / `OpenHarmony-7.0.0.105` / musl / 非 root
- 移植基线（社区公开）：`ohos_gecko-opensource`，mozilla-central **142.0a1**（pinned `5836a062…`，2025-07-08 快照）+ 84 个移植 commit + v271 补丁序列，MPL-2.0

---

## 0. 一句话结论

**这台机器的"移植工作站"底子是够的**（DevEco 26 + API 26 SDK/NDK 齐备、签名通道打通、网络可达、磁盘充足，且已有 HandBrake 等在真机上跑通的先例）。
但**现在还开不了工**，缺 3 件可补齐的东西：

| # | 缺口 | 性质 | 补齐成本 |
|---|---|---|---|
| ① | **Linux 构建主机**（WSL2 未启用；Gecko 的 `mach` 不能在 Windows 上交叉编到 OHOS） | 硬门槛 | 需管理员 + 一次重启，之后 30 min |
| ② | **Rust 工具链 + `aarch64-unknown-linux-ohos` target** | 硬门槛 | 在 ① 里装，约 10 min |
| ③ | **Gecko 源码 / 移植仓**（本机完全没有；现有下载只有 `Firefox Setup 152.0.1.exe` 安装包） | 硬门槛 | 约 2–3 GB 下载，20–60 min |

另有 1 项**不是环境问题、但决定项目成败**的发现：**公开移植仓目前"跑不通"**——README 明确说明还差约 **1029 个共享上游文件**的适配与 **171 个 OHOS 专属新文件**未公开（`docs/UPSTREAM.md §4` 是最优先补齐项）。也就是说环境就绪后，第一步能拿到的是"编译链 + 补丁资产 + 明确的缺口清单"，而不是一个开箱即用的 Firefox。

> 结论分层：**环境满足度 ≈ 80%（补齐 ①②③ 即到 100%）；可复现资产满足度 ≈ 30%（受限于公开仓缺口，与这台机器无关）。**

---

## 1. 判定口径（"满足"是相对什么说的）

Firefox/Gecko 移植到 HarmonyOS 的硬性依赖，来自上游与社区工程实测：

1. **构建主机**：Gecko 用 `mach` + `mozbuild` 构建，官方只支持 Linux / macOS / Windows(MSVC)。OHOS 是交叉编译目标，社区链是 POSIX 脚本（`build_firefox.sh`、`preflight.sh`），**必须在 Linux/macOS 上跑**；Windows + MSYS2 不在支持范围。
2. **工具链**：HarmonyOS SDK/NDK（`<SDK>/native` 下 `llvm/` + `sysroot/`）、Rust + `aarch64-unknown-linux-ohos`、**python3.11**（README 实测 3.14 会让 mach 内部 ast 解析崩）、mozbuild 自持 host clang（`~/.mozbuild/clang`）、`git`。
3. **设备**：能 `hdc` 连接、开发者模式、API ≥ 移植层要求的 OHOS 版本（本机 API 26 满足 2026 年 targetSdkVersion 26 的新规）。
4. **签名**：零售鸿蒙只认**华为签发**的 profile（bundleName + 设备 UDID 双匹配）；OpenHarmony 自签链会被拒（HandBrake 移植已证伪）。
5. **资源**：Gecko 源码树 + objdir 体量大（社区作者本机：源码树 27 GB、obj 22 GB）；磁盘建议 ≥ 100 GB 空闲。

---

## 2. 已满足项（绿）

| 项 | 实测结果 | 结论 |
|---|---|---|
| 操作系统 | Windows 11（内部版本 26300，家庭中文版），64 位 | ✅ 可跑 DevEco/hvigor/hdc |
| CPU | AMD Ryzen 7 7840H，8 核 / 16 线程 | ✅ 全量 Gecko 构建可用 `-j8~12`，不霸占整机 |
| 内存 | 29.7 GB | ✅ 够用（Gecko 链接期吃内存） |
| 磁盘 | C: 空闲 **575.7 GB**；D: 空闲 **459.9 GB** | ✅ 远超 100 GB 需求 |
| 硬件虚拟化 | `VirtualizationFirmwareEnabled=True`，VBS 运行中 | ✅ WSL2 前提满足 |
| DevEco Studio | 26.0（`261.23567.138.36.2600851`），`C:\Program Files\Huawei\DevEco Studio` | ✅ 与 API 26 配套 |
| HarmonyOS SDK | `sdk\default\openharmony`：`apiVersion=26`、`platformVersion=26.0.0`、`version=26.0.0.105`（Release）；`hms` 同版本 | ✅ **正好是 API 26** |
| OHOS NDK | `<SDK>/native`：`llvm/`、`sysroot/`（`aarch64-linux-ohos`，musl）、`build-tools/cmake`（CMake 3.28.2 + ninja）、clang **15.0.4**、`ld.lld` | ⚠️ 可用，但 clang 版本偏低（见 P1-1） |
| hvigor / ohpm / node | `tools\hvigor\bin\hvigorw.bat`、`tools\ohpm\bin\ohpm.bat`、Node **v24.14.1** | ✅ HAP 打包链完整 |
| hdc | `sdk\default\openharmony\toolchains\hdc.exe`，**Ver 3.2.0f** | ✅ 可连真机 |
| Java | Microsoft OpenJDK 25（另有 DevEco 自带 JBR） | ✅ 签名/HAP 工具可跑 |
| 签名通道 | **HO-Kit 已登录华为开发者账号**（`%LOCALAPPDATA%\ho-kit\auth\user_info.json`），调试证书有效期至 **2027-09-12**；已为 8 个不同 bundleName 申请过华为调试 profile（含 `com.handbrake.ohos`） | ✅ **可为本项目新 bundleName 申请 profile** |
| 移植先例 | HandBrake（真机跑通转码）、Aegisub、Pixez、Arcaea、Geekbench、VintagePomeloPro 等均有签名产物 | ✅ 这台机器是成熟的 OHOS 移植工作站 |
| 网络 | 直连可达 github.com、hg.mozilla.org、developer.huawei.com、repo.huaweicloud.com、ohpm.openharmony.cn、gitcode.com、static.rust-lang.org；下载实测 **≈2.7 MB/s**（mozilla/rust 官方源） | ✅ 无代理依赖 |
| MSYS2 | `C:\msys64`：gcc 15.3.0、Python 3.12.15、nasm 3.02、yasm 1.3.0、make 4.4.1、perl 5.42、git 2.45.1 | ✅ 辅助工具齐（Windows 侧用） |
| git / 源码获取 | git 2.45.1；`git ls-remote` 已验证 gitcode 移植仓可匿名访问 | ✅ |
| 模拟器 | DevEco Emulator 26.0 + HarmonyOS 7.0.0 **PC x86** 镜像（MateBook Pro 2in1 配置） | ⚠️ 仅 x86 PC 镜像，跑不了 arm64 原生库；**真机必需** |
| 历史项目资料 | `docs\HandBrake移植鸿蒙心得.md`（20 条踩坑，含 musl/HAP/签名/SELinux 结论）可复用 | ✅ |

---

## 3. 缺口与风险（红/黄）

### P0-1 Linux 构建主机缺失（硬门槛）

- 现状：`Microsoft-Windows-Subsystem-Linux`、`VirtualMachinePlatform` 均为 **Disabled**（`Win32_OptionalFeature.InstallState=2`）；无任何 WSL 发行版；`wsl --status` 无输出。
- `D:\vm\machine`、`D:\vm\disk\ubuntu.vhdx`（12.4 GB）是**旧 Hyper-V 残留**：本机是**家庭版**，Hyper-V 角色不可用（`vmms`/`Get-VM` 均不存在），这些资产**无法直接启动**。
- 为什么必须：Gecko 的 `mach`/`mozbuild`、社区移植脚本、`preflight.sh` 全是 POSIX；**Windows 上没有受支持的 OHOS 交叉编译路径**（MSYS2 只适合辅助，不能替代）。
- 解法（推荐）：启用 WSL2 → 安装 **Ubuntu 24.04 LTS**（Python 3.12 在 Gecko 支持区间；避免 3.14）。
  - 需要**管理员权限**，启用功能后**需要一次重启**——这是唯一会"影响使用"的动作，建议约在你不用机器的时间窗。
- 备选：你另有一台 Linux 主机/服务器，我远程对接；或装 VirtualBox/VMware（同样要管理员 + 装软件，且嵌套虚拟化更折腾）。

### P0-2 Rust 工具链缺失（硬门槛）

- 现状：`rustc` / `cargo` / `rustup` 全部缺失（MSYS2 里也没有）。
- 需要：在 Linux（WSL）内 `rustup` + `rustup target add aarch64-unknown-linux-ohos`。OHOS 三目标已升为 **Tier 2 with host tools**（2025 年 Rust PR 通过），stable 渠道可直接装 std。
- 版本以 `mach configure` 的要求为准（Gecko 142 期对应 rustc 1.8x 量级），rustup 会自动按源码要求装。

### P0-3 Gecko 源码 / 移植仓未获取（硬门槛）

- 现状：本机无任何 mozilla/gecko 源码或移植仓（只有 `Firefox Setup 152.0.1.exe` 安装包）。
- 需要的资产：
  1. 移植仓发布视图（`gitcode.com/OpenHarmonyPCDeveloper/ohos_gecko-opensource`，91 个文件：补丁序列 + 3 个 OHOS 专属目录）；
  2. 上游 pinned revision（`5836a062…`）的源码树，建议 `git fetch --depth 1 <sha>`（约 1–2 GB，2.7 MB/s 下约 10–15 min）。
- 注意：**不要**把 27 GB 的完整树塞进中文路径；按 HandBrake 的教训，构建树/工程一律放 **ASCII 路径**（建议新建 `D:\ff-ohos\`），中文目录只放 junction/文档。

### P0-4 真机当前未连接（不阻塞开工，阻塞验收）

- 现状：`hdc list targets` → `[Empty]`；上次无线地址 `192.168.1.3:38247` 不可达；本机 WLAN 为 `192.168.1.5/24`（同网段，设备可能只是关机/未开无线调试）。
- 需要：开机 → 开发者模式 + USB 调试（或 `hdc tconn <ip>:<port>`）。签名 profile 里的 `device-ids` 必须包含该机 UDID（`hdc shell bm get --udid`，历史值 `42DF49EC…`）。

### P1-1 Clang 版本偏低（需在构建链中解决）

- 现状：本机 OHOS NDK 自带 clang **15.0.4**；上游自 2025-08 起最低要求 **Clang 17**（[Bug 1981918](https://bugzilla.mozilla.org/show_bug.cgi?id=1981918)），Gecko 142 期已在门槛线上。
- 社区移植链的做法：**mozbuild 自持 host clang**（`~/.mozbuild/clang`）负责主机侧工具，目标侧依赖 NDK；若目标编译也强制 ≥17，则需换成新版 NDK/clang 或走移植仓的 toolchain 补丁。
- 结论：不是环境"没有"，而是**要在 `preflight.sh` 里实测确认**；若报版本错，优先补 Python/clang 而不是硬改检查。

### P1-2 Python 版本窗口

- 需要 **3.11–3.13**（README：3.14 会让 mach 内部 ast 崩）。Ubuntu 24.04 默认 3.12 → ✅ 直接满足；不要用 25.10+ 的 3.14。

### P1-3 移植资产不完整（最关键，非环境问题）

公开仓 README 原文要点：

- 产物：`libxul.so` + `libgeckoview.so`（单进程、单 Surface 的**嵌入式内核**，不是完整桌面 Firefox）；同线承载"Firefox 浏览器本体"与 Zotero 9.0.6。
- 配套：`widget/openharmony`（51 文件）、`ports/ohos`（6 文件，`geckoview.cpp` 4484 行）、`mobile/ohos`（34 文件）、`patches/01–09` + `full/`（v1→v271：1126 文件 / +86,519 行 / −7,283 行 / 257 新建）。
- **⚠️ 复现链"目前跑不通"**：补丁只覆盖 2026-09-25 基线之后的改动；基线之前还有约 **1029 个共享上游文件**的适配（third_party 521、media 166、browser 120…）与 **171 个 OHOS 专属新文件**（`build/moz.configure/ohos-ndk.configure`、`gfx/thebes/gfxOHosPlatform.*`、`ipc/chromium/src/base/message_pump_ohos.*`、`media/libcubeb/src/cubeb_ohaudio.cpp` 等）不在仓内；`docs/UPSTREAM.md §4` 给出两条补齐路径，并称这是"当前最优先的补齐事项"。
- 含义：环境就绪后，**第一目标应是"把 preflight/configure 跑通 + 用发布资产复现到卡点"，同时摸清 1029/171 的补齐量**；完整 Firefox 内核的时间成本以"人月"计，不是"一夜编译"。
- 另一条现实路径：与社区作者/群（README 载明 QQ 群 **1105698553**）同步，或用 `docs/UPSTREAM.md §4` 的补齐路径先做**最小可运行内核 Demo**（黑屏/首帧/输入三件事）。

### P1-4 兼容性 / 合规

- 设备是 **HarmonyOS 7 / API 26**（2026-10 刚推送），移植基线是 2025-07 的 Gecko 142；社区兼容矩阵（2in1/平板/手机）需按 API 26 重新验证：平板上已知"手机沙箱禁 `memfd_create`"的限制不适用（平板不禁），但 `64K PT_LOAD` 对齐、`nativeLib.strip:false`、禁止二进制 `patchelf`（musl `reloc_all` 崩）等打包纪律必须遵守。
- 品牌：Firefox 名称/图标为 Mozilla 商标，MPL-2.0 允许改源分发但**不允许直接沿用品牌打包分发**；社区同类项目改用 Iceweasel 等独立品牌。建议先定"内部研究版（不上架）"还是"可分发版（换品牌）"。

---

## 4. 上游与社区现状（为什么"可行"但"很难"）

| 事实 | 对项目的意义 |
|---|---|
| Mozilla **官方不支持** OHOS（社区在 Mozilla 支持论坛长期请愿，无官方 target） | 必须走社区移植层，无官方兜底；升级/安全修复需自行 rebase（移植仓跟随 mozilla-central 周更，换基线要重放 1100+ 文件） |
| 公开工程 `ohos_gecko-opensource`（2026-10 公开）：mozilla-central 142.0a1 + 84 commits + v271 补丁；自研窗口平台层 + NAPI 桥 + WebRender→XComponent 渲染 | **可行性已被证明**（连 Firefox 壳、Zotero 都能跑），这是本项目的直接参考/基线 |
| 另一份"Gecko→OHOS 移植指南"（Codeberg `CoreMobile/GeckoDemo`）只有架构说明，无实体代码 | 只能当思路，不能当资产 |
| 社区 `build_in_harmonyos` 已完成 **mozjs（SpiderMonkey 140 ESR）** 的 HarmonyOS PC 适配（conan 交叉编译） | 说明引擎级组件可交叉编译；但离"浏览器内核 + 壳"还差平台层 |
| WebKit-for-OpenHarmony（WPE/Cerbero）、Servo-for-OHOS 先例 | 平台层工作量参照：图形/输入/生命周期桥是大头 |
| Alpine 用 clang 20 + musl 构建 Firefox 142 | musl 不是死路，但需要补丁 |

---

## 5. 建议执行路线（分阶段，先静默后打扰）

> 原则：**所有不需要重启的准备工作现在就静默做完；需要管理员/重启的动作留给你指定的时间窗。**

**阶段 0（现在可静默做，不重启、不装东西）**
1. 建 ASCII 工作根 `D:\ff-ohos\`（`src\`、`port\`、`out\`、`logs\`）。
2. 克隆移植仓发布视图（91 文件级别，几十 MB）。
3. 浅取上游 pinned revision 源码（约 1–2 GB）。
4. 只读分析：`patches/README.md`、`docs/UPSTREAM.md`、`build/preflight.sh`，输出"缺口清单 + 构建前置条件"。
5. 更新本报告的"阶段 1 命令清单"为可直接执行的脚本（等你授权）。

**阶段 1（需你授权：管理员 + 一次重启）**
```powershell
# 管理员 PowerShell
wsl --install -d Ubuntu-24.04
# 重启后
wsl --set-default-version 2
```
```bash
# WSL(Ubuntu) 内
sudo apt update && sudo apt install -y build-essential python3.11 python3.11-venv \
  pkg-config libssl-dev libffi-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
  clang lld llvm git curl unzip zip cmake ninja-build
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add aarch64-unknown-linux-ohos
```
**阶段 2（静默长任务，建议夜间）**
- `bash build/preflight.sh` → 记录缺项；`mach configure`（只验证工具链，不跑全量 build）。
- 首次全量 `libxul` 构建（8C/16T 估计 1–3 h，obj 20–40 GB）。

**阶段 3（项目主体）**
- 按 `docs/UPSTREAM.md §4` 补 1029+171 资产，或拿到作者完整树；
- 产出 `libxul.so` + `libgeckoview.so`。

**阶段 4（HAP + 真机）**
- 建 ASCII 路径 HAP 工程（参照 HandBrake 的 NAPI 样板 + 社区 `mobile/ohos` 装配）；
- `targetSdkVersion 26.0.0`；`nativeLib.strip:false`；注入 `.permission` 段后做 ELF 对齐修复；
- HO-Kit 申请新 bundleName 调试 profile → 签名 → `hdc install -r` → `aa start` → 用 `uitest dumpLayout` + hilog 验收（首帧、输入、不崩）。

---

## 6. 需要你提供的 4 件事

1. **管理员权限 + 一个重启时间窗**（装 WSL2；一次即可）。
2. **华为开发者账号**：HO-Kit 里已登录（开发者 ID `2037…7296`，证书 2027-09-12 到期）——确认继续用它申请本项目的调试 profile 即可；若换账号需重新登录。
3. **真机接入**：开机后开开发者模式 + USB 调试，或同一 Wi-Fi 下把 `hdc tconn` 地址给我（上次 `192.168.1.3:38247` 已失效）。
4. **两个决策**：
   - 目标形态：先做"内核 Demo（黑屏→首帧→输入）"验证，还是直接冲"完整 Firefox 壳"（工作量大一个数量级）；
   - 品牌/合规：内部研究版可直接用 Firefox 名；若将来分发，需换品牌（Iceweasel 等）或取得 Mozilla 授权。

---

## 7. 资源预算（基于实测）

| 项 | 数值 |
|---|---|
| 磁盘 | 建议预留 100 GB；本机 D: 有 459.9 GB 空闲 |
| 下载带宽 | ≈2.7 MB/s（mozilla/rust 官方源实测） |
| 阶段 0 下载 | 移植仓 <100 MB + 源码 1–2 GB → 约 10–20 min |
| 阶段 1 安装 | WSL2+Ubuntu 3–5 GB 下载/安装 + 重启 |
| 构建时间 | 首次 configure 5–15 min；全量 libxul 1–3 h（8C/16T）；增量 5–20 min |
| 真机验收 | 签名 1–2 min，安装+首启动 <1 min |

---

## 8. 本次体检做过什么、没做什么（静默承诺）

**做过（全部只读）**：系统/硬件/磁盘、DevEco/SDK/NDK 版本、hvigor/ohpm/hdc/node、Java/MSYS2/git、网络可达性与下载测速（仅 8 MB 测速临时文件，已删）、注册表可卸载列表、HO-Kit 签名材料清单（未读取账号令牌内容）、WSL/Hyper-V 状态、真机 hdc 在线状态、社区移植工程公开文档。

**没做**：没有安装/卸载任何软件，没有改注册表/环境变量/PATH，没有启动 DevEco/HO-Kit/模拟器等 GUI，没有下载任何大文件，没有修改本机现有 HandBrake 工作区，没有连接/操作真机。唯一写入：本报告。

---

## 9. 复核命令（可随时自己跑）

```powershell
# 设备
& "C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe" list targets
# SDK 版本（应为 26）
Get-Content "C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\ets\oh-uni-package.json"
# NDK clang
& "C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\native\llvm\bin\clang.exe" --version
# WSL 功能状态（2=Disabled）
Get-CimInstance Win32_OptionalFeature -Filter "Name='Microsoft-Windows-Subsystem-Linux' OR Name='VirtualMachinePlatform'" | Select Name,InstallState
# 磁盘
Get-PSDrive C,D | Select Name,@{n='FreeGB';e={[math]::Round($_.Free/1GB,1)}}
# 签名材料
Get-ChildItem "$env:LOCALAPPDATA\ho-kit\sign\provisions" | Select Name
```

---

## 10. 参考链接

- 社区 Gecko 移植工程（本项目基线）：<https://gitcode.com/OpenHarmonyPCDeveloper/ohos_gecko-opensource>
- Mozilla 官方无 OHOS 支持（社区请愿）：<https://support.mozilla.org/ne-NP/questions/1582896>
- Gecko 最低 Clang 17（上游变更）：<https://bugzilla.mozilla.org/show_bug.cgi?id=1981918>
- Rust OHOS 目标升 Tier 2（含 std）：<https://rust.googlesource.com/rust/+/227690a258492c84ae9927d18289208d0180e62f>
- HarmonyOS 7 / API 26 升级适配（官方）：<https://developer.huawei.com/consumer/cn/doc/doccenter-release-notes/upgrade-adaptation>
- HarmonyOS 7（API 26）快速适配指南（官方论坛）：<https://developer.huawei.com.cn/consumer/cn/forum/topic/0208227805407896221>
- Gecko→OHOS 移植思路参考（无实体代码）：<https://codeberg.org/CoreMobile/GeckoDemo>
- SpiderMonkey 140 ESR 的 HarmonyOS PC 适配（引擎级先例）：<https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos/merge_requests/17266>
- 鸿蒙 PC 官方 Linux 虚机"融合开发引擎"（仅鸿蒙 PC，不适用本机/平板）：<https://linux.do/t/topic/1885831>
- 本机已有移植经验：`docs\HandBrake移植鸿蒙心得.md`（签名/沙箱/HAP 打包 20 条踩坑）

---

## 11. 勘误与进展（2026-11-17 13:20 更新）

体检后已拉取移植仓发布视图（`D:\ff-ohos\port\ohos_gecko`，116 文件 / 8.4 MB），据此修正与更新：

1. **资产缺口比报告正文小**：README 说的"跑不通"指 `patches/01–09` 分组链（其基线是未公开的 v151 快照 commit `7458d382eb`）；而 `patches/full/ohos-v271-vs-upstream-5836a062726f.patch`（5.39 MB，1126 文件 / +86k 行 / 257 新建）**已在公开仓**，作者实测 `git apply --check` 对上游 pinned revision `5836a062726f` 干净通过。→ **内核源码层可按 `docs/UPSTREAM.md §4.1` 一步重建**，正文 P1-3 的"1029+171 文件缺失"判断作废。
2. **仍缺的公开资产**：`build/` 目录（mozconfig、`build_firefox.sh`、`preflight.sh`、`post_build.sh`）在 MANIFEST 里但**不在 git 树**中；宿主 HAP 工程（ArkTS 壳）也未公开。前者可按 `UPSTREAM.md §3.4` 的动作清单重建，后者需自建（NAPI 契约以 `platform/ports/ohos/geckoview.cpp` 为准）。
3. **Python 版本**：移植仓明确要求 **python3.11**（Ubuntu 24.04 默认 3.12）→ 引导脚本已改为 deadsnakes PPA 安装 3.11。
4. **SDK 版本**：移植仓声明 `targetSdkVersion = 6.1.0(23)`，本机设备为 **API 26** → HAP 需升到 `26.0.0` 后验证（API 26 行为变更风险需实测）。
5. **签名风险（最关键）**：JIT 受限 ACL 权限三处缺一即 `XRE_main` 早期 MOZ_CRASH：`module.json5` 声明 + `.permission` ELF 段 + **调试 profile 的 ACL**。HO-Kit 能否签发带 ACL 的调试 profile 尚未验证；退路是首版走 `--airweb-force-no-jit`（慢，但可先跑通链路）。
6. **Rust target**：移植仓文档按 tier3（`-Z build-std` 或自带 std sysroot）描述；上游 Rust 已把 OHOS 三目标升为 tier2 with host tools，先试 `rustup target add aarch64-unknown-linux-ohos`，不行再按文档处理。
7. **环境进展**：WSL 两个 Windows 功能已启用（DISM 3010），`CBS_RebootPending=True`，待用户重启；用户已批准"重启后弹一次 UAC（方案 A）"安装 WSL 本体 + Ubuntu 24.04。施工状态见 `D:\ff-ohos\logs\status.md`。
