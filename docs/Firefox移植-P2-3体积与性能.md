# Firefox / Gecko for HarmonyOS —— P2-3 体积与性能（第一版）

> 时间：2026-11-18 · 目标：压缩 HSP 体积、确认启动不退化

## 一、体积优化结果

| 项 | 优化前 | 优化后 | 说明 |
|---|---|---|---|
| gecko libs（arm64-v8a） | 302.1 MB（原始）/ 约 352 MB 含未 strip | **224 MB** | `llvm-strip --strip-unneeded` 全量 strip，备份在 `artifacts/libs-backup-p23` |
| omni.ja | 65.5 MB（STORED） | **21.4 MB**（deflate -6） | Gecko Omnijar 支持 deflate，实测可正常加载 |
| **HSP 安装包** | **292.3 MB** | **250.2 MB（-42.1 MB, -14.4%）** | 改后真机安装、启动、页面加载均正常 |

明细（strip 后）：libxul 193.5MB、mozjs 14.4MB、gkcodecs 6.4MB、mozavcodec 3.3MB、mozsqlite 1.4MB、其余 NSS/NSPR 若干。

## 二、启动性能

同一测量方法（`aa start` → 轮询 hilog `first-composite`，冷装首次启动）：

| 配置 | 首帧耗时 |
|---|---|
| STORED omni（292MB） | 5890 ms |
| deflated omni（250MB） | 5858 ms |

结论：**omni 压缩未带来可测量的启动退化**（差异在测量噪声内）；strip 只影响符号表，不影响加载。

## 三、到 ≤200MB 的路径（需要引擎重编）

当前 250MB 主要构成：libxul 193.5 + mozjs 14.4 + 其它 libs ~16 + omni 21.4。

可行手段：
1. **引擎重编裁剪**（最大头）：
   - `--disable-webrtc`、`--disable-webspeech`、`--disable-media-*`（视需求保留基础解码）；
   - 裁掉 gkcodecs/mozavcodec（若走系统媒体解码，可省 ~10MB）；
   - 目标 libxul 降低 20–35MB；
2. 语言包/资源裁剪（omni 再降 3–8MB，注意保留 zh-CN/en-US）；
3. 打包侧压缩 .so（HarmonyOS 安装会解压到 libs 目录，HSP 可更小，需验证签名/安装链路）；
4. 拆分"HSP + 按需资源包"。

## 四、风险与注意

- strip 备份在 `D:\ff-ohos\artifacts\libs-backup-p23`（若后续排查回溯需要，可从备份恢复）；
- omni 改为 deflate 后，`build-omni.sh` 默认仍是 STORED；当前项目 rawfile 中已是 deflate 版本，重建需用 `zip -6`；
- 媒体能力未验证（gkcodecs/avcodec 仍在包内，媒体页应可播放，但未做长视频测试）。

---

## 七、P2-3 v2（引擎重编 ≤200MB）：尝试记录（2026-11-18 14:20）

### 尝试的裁剪配置（备份：/home/dev/ff/gecko/mozconfig.p23-trim）
`
--enable-optimize="-Os"
--disable-webrtc
--disable-parental-controls
--disable-geckodriver
--disable-profiling
`

### 结果：**未通过，已回退**
1. --disable-webcodecs / --disable-webgpu / --disable-perfetto 在该分支为**未知配置项**（configure 拒绝）；
2. --disable-accessibility 会导致 PDocAccessible.ipdl 找不到 DocAccessibleTypes.ipdlh，ipdl 导出失败；
3. 去掉上述项后，gkrust 的 uild_gecko::generate（bindgen）**panic**，Rust 库构建失败（orce-cargo-library-build Error 101）。

### 结论与后续
- 仅靠 mozconfig 裁剪 + -Os 在当前移植分支上会触发 ipdl/bindgen 兼容问题，需要逐项适配（例如先只加 --disable-webrtc 单变量验证、或修补 	oolkit/components/... 的 bindgen 调用）；
- 已回退到稳定配置（原 --enable-optimize），设备与产物仍为 v1 的 250.2MB 构建，未受影响；
- 若继续冲 ≤200MB，建议按"最小变量"迭代：单加 --disable-webrtc → 验证构建与运行 → 再叠加下一项；每次记录 libxul/HSP 体积。
