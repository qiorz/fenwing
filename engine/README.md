# engine/ — Gecko 侧：基线、补丁、复现

这个目录只回答一个问题：**「那 185 MB 的 `libxul.so` 和 20 MB 的 `omni.ja` 是怎么来的？」**

## 基线

| 项 | 值 |
|---|---|
| 上游 | mozilla-central（Firefox `142.0a1`） |
| pinned commit | `5836a062726f715fda621338a17b51aff30d0a8c`（2025-07-08） |
| target | `aarch64-unknown-linux-ohos` |
| 工具链 | OpenHarmony 7 native SDK（clang/LLVM，API 26）+ Rust stable |
| 构建宿主 | WSL2 Ubuntu 24.04，`./mach build -j8` |
| 实测耗时 | 33 分 42 秒（8 vCPU），`libxul.so` 3.5 GB → strip 185 MB（v1.3 起 176 MB） |

## 补丁

```
patches/firefox-ohos-gecko-5836a06272.patch      5.7 MB   1139 个文件
patches/firefox-ohos-gecko-5836a06272.patch.gz   1.1 MB   （同一份，gzip）
```

这是**整树快照**：对 `5836a062` 检出的 diff，包含

- 新增平台层 `widget/openharmony/`（`nsAppShell`、`nsWindow`、`OHOSNativeWindowBridge`、
  `OHOSClipboard`、`OHOSMenuBridge`、`OHOSChromeBridge` …）
- 新增 `ports/ohos/`（NAPI 宿主、输入、IME、下载、菜单、`libxul.symbols` 导出）
- 新增 `dom/media/platforms/ohos/`：`OHOSDecoderModule` / `OHOSVideoDecoder`，
  H.264/HEVC 硬件解码（OH_AVCodec Buffer 模式；PDM 优先硬解、失败回退 FFmpeg）
- `gfx/` WebRender / EGL 合成改造、`layout/` 移动视口与 paint holding、
  `browser/` chrome ArkTS 化（`ohos-chrome-bridge.js`、`phone-chrome`）、
  `xpcom/` 线程与 `Omnijar` 适配、`build/moz.configure` 的 OHOS target 识别
- 本工程的 P0–P2 修补：JIT 探测与降级、标题/URL 同步契约、`omni.ja` 目录形式传参、
  `geckoview.js` 的内容区菜单构造（新标签打开、保存图片、复制地址等菜单项）

### 为什么是整树补丁而不是提交序列

本地那棵 23 GB 的 Gecko 树是 **浅克隆 + 未提交工作区**（1 个 commit，约 1000 个未提交改动），
没有可移植的提交历史。社区移植仓库 `ohos_gecko` 虽然提供了按子系统拆分的补丁，
但其补丁是 CRLF 行尾、且与 `5836a062` 的上下文已经漂移，无法在纯净检出上直接 `git apply`。

所以我们发布**能精确重建本工程内核树的那一份 diff**：它不漂亮，但它可验证。

## 已验证

在 `/tmp` 里重新检出 `5836a062`（387,841 个文件），应用本补丁，再与构建机的树逐文件比对：

```
APPLY_OK
compared=1139 mismatches=0
```

v1.0 / v1.1 / v1.2 / v1.3 每次发布前都跑过同样的验证（v1.3 的差异是硬件解码模块、
`--disable-webrtc` 与 `omni.ja` 打包方式）。

## 应用

```bash
git clone --filter=blob:none --no-checkout https://gitee.com/mirrors/gecko-dev.git gecko
cd gecko
git fetch --depth 1 origin 5836a062726f715fda621338a17b51aff30d0a8c
git checkout 5836a062726f715fda621338a17b51aff30d0a8c

git apply -p1 ../engine/patches/firefox-ohos-gecko-5836a06272.patch
```

或直接跑 [`apply-port.sh`](apply-port.sh)。

## 构建

```bash
# 依赖：OHOS native SDK（/opt/ohos-sdk/native）、Rust、clang、python3、autoconf 等
cp ../engine/mozconfig ./mozconfig
export OHOS_SDK_NATIVE=/opt/ohos-sdk/native
./mach build -j$(nproc)
```

产物在 `obj-aarch64-unknown-linux-ohos/dist/bin/`：

```
libxul.so            3.5 GB（未 strip；--disable-webrtc 构建 strip 后 176 MB）
libgeckoview.so      620 KB
libnspr4/libnss3/libgkcodecs/libmozjs…   14 个运行时依赖
```

### 瘦身（P2-3）

```bash
# 1) strip 所有运行库（302 MB -> 213 MB）
bash ../scripts/p23-strip.sh

# 2)（可选）omni.ja 用 deflate 重打（65.4 MB -> 约 20 MB）
#    当前 v1.3 构建用的是 STORED（62 MB）；要瘦身需手工执行同一份条目表：
cd obj-aarch64-unknown-linux-ohos/dist/bin
zip -6 -r -X /tmp/omni.ja \
  chrome defaults components modules res actors hyphenation localization dictionaries \
  platform.ini chrome.manifest greprefs.js application.ini
cp /tmp/omni.ja /path/to/app/gecko/src/main/resources/rawfile/omni.ja
```

### JIT（可选）

```bash
llvm-strip --strip-unneeded libxul.so -o libxul-stripped.so
llvm-objcopy --add-section .permission=ports/ohos/permission.json \
             --set-section-flags .permission=readonly libxul-stripped.so libxul-jit.so
```

再执行 [`../scripts/stage-engine.sh`](../scripts/stage-engine.sh) 把库和 `omni.ja` 铺回
`app/gecko/libs/arm64-v8a/` 与 `rawfile/`，最后用 `scripts/build-all.ps1` 出包。

> ⚠️ `omni.ja` 不是普通 zip：它是 mozjar 生成的 GRE 资源包，必须整体放进 `rawfile/`，
> 运行时复制到沙箱再以目录形式传给 `-greomni`。**别解压、别反编译后重打**。

## 来源与归属

见 [PROVENANCE.md](PROVENANCE.md)。
