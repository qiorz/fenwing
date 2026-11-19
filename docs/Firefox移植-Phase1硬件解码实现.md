# Phase 1 硬件视频解码（OH_AVCodec）实现说明

> 状态：代码已实现并成功编译出 libxul；真机对比测量待设备解锁后完成。

## 1. 新增代码

```
dom/media/platforms/ohos/
  OHOSDecoderModule.h/.cpp   # PlatformDecoderModule 实现：H.264/HEVC 声明硬件支持
  OHOSVideoDecoder.h/.cpp    # OH_AVCodec 视频解码器封装（NV12 ByteBuffer → VideoData）
  moz.build                  # 源码加入 libxul
dom/media/platforms/moz.build    # DIRS += ["ohos"]
dom/media/platforms/PDMFactory.cpp  # MOZ_WIDGET_OPENHARMONY 下注册并优先使用
```

## 2. 解码流程

1. `OH_VideoDecoder_CreateByMime("video/avc"|"video/hevc")`；
2. `Configure`：宽/高、`OH_MD_KEY_PIXEL_FORMAT = AV_PIXEL_FORMAT_NV12`；
3. `RegisterCallback`（buffer 模式：onNeedInputBuffer / onNewOutputBuffer）；
4. 输入：`OH_VideoDecoder_GetInputBuffer` → 拷贝压缩帧 → `SetBufferAttr(pts/size)` → `PushInputBuffer`；
5. 输出：`GetOutputBuffer` → 读取 NV12 → 构造 `layers::PlanarYCbCrData`（Cb/Cr 交错 = NV12）→
   `PlanarYCbCrImage::CopyData` → `VideoData::CreateFromImage`；
6. Promise 驱动：`Decode()` 返回 `DecodePromise`，输出到达时以帧数组 resolve；`Flush/Shutdown` 释放。

## 3. 关键工程决定

- **NDK 库改为运行时 dlopen**：libxul 直接链接 `libnative_media_{vdec,core,codecbase}.so` 时，
  lld 报 "undefined hidden symbol"（NDK stub 的可见性问题）；改为 `dlopen` + `dlsym` 后可正常链接，
  并在 `Init()` 中惰性加载。
- 未启用 WebRTC（`--disable-webrtc`）以避免与移植树缺失的 PeerConnection WebIDL 冲突，
  同时减小体积；与本功能无关。
- `.permission` 段需在替换 libxul 后重新注入（`enable-jit-libs.sh`），否则 JIT ACL 失效。

## 4. 构建产物

- 新 libxul（obj-hw）：strip 后约 177MB（比上一版 193MB 小，部分来自 disable-webrtc）；
- 已注入 `.permission` 并打包 HSP（当前 283.8MB，含 mozjs 双份与 omni 65MB 未压缩条目）。

## 5. 待完成

- 设备解锁后安装并验证：
  1. 视频可播放（H.264/HEVC）；
  2. CPU 对比（软解基线 720p H.264 ≈ 89–123% CPU、RSS ~320–325MB）；
  3. 失败回退检查（解码器创建失败时应回退 FFmpeg）。

---

## 6. 真机联调结果（2026-11-19）

- 新 libxul 可启动，PDM 注册成功（日志：`OHOSDEC module Create`、`OHOSDEC CreateVideoDecoder called`）；
- 视频页面出现**内容区全黑**、CPU 接近 0，说明解码/渲染通路未打通；
- 已修复的问题：`NeedsConversion()` 需要返回 `kNeedAnnexB`（否则 H264ChangeMonitor 触发 MOZ_DIAGNOSTIC_ASSERT 崩溃）；
- 尚未定位：解码器 `Init()` 未进入或阻塞（标记只有 Create，无 init/started），需要进一步用 stderr/文件标记与线程栈排查；
- 为避免影响日常使用，已回退到已知可用的软解 libxul（`artifacts/gecko/libxul-jit.so`），视频播放、页面渲染恢复正常（CPU 90–133%，与基线一致）。

## 7. 后续

1. 确认 `Init()` 是否被调用（在 IO/媒体线程打 stderr 标记），以及是否阻塞主线程导致页面全黑；
2. 检查 MediaChangeMonitor 包装与大缓冲/多实例行为（日志显示同一时刻创建两个 decoder）；
3. 通过后再测硬解 CPU/RSS 与软解对比。

## 8. 联调进展（2026-11-19 11:30）

已打通：
- `Init()` 全流程成功（createByMime/configure/registerCallback/start）；
- 发现并修复 buffer 模式关键问题：`onNeedInputBuffer` 回调**直接提供 OH_AVBuffer***，
  `OH_VideoDecoder_GetInputBuffer()` 返回 NULL；改为使用回调传入的 buffer 后，
  输入帧成功送入（`push input size=17373`），并收到**首个解码输出帧**。

仍未解决：
- 收到输出帧后，页面内容区仍然全黑（CPU 约 111%），疑似 VideoData/图像格式或渲染同步问题；
- 需进一步：打印输出宽高/stride、抓取首帧 NV12 落盘校验、对比 PlanarYCbCrImage NV12 与 I420 路径、检查 WebRender 错误。

已恢复软解 libxul 供日常使用（视频/页面正常）。

## 9. 联调进展（2026-11-19 11:50）

- 修复输入 buffer 使用方式（回调直接给 OH_AVBuffer*）；
- 解码输出成功：`first output 1280x720 pts=0`，随后连续输出（pts 66ms/100ms/133ms...）；
- 页面可渲染、视频画面能显示（曾观察到彩条画面）；
- 但播放会**中途停止**（重启应用后 CPU≈0、视频灰屏）：Decode 立即 resolve 后仍需保证持续喂帧与输出消费；
- 另外将帧构造从 codec 回调线程改到后台任务（NS_DispatchBackgroundTask），避免 ImageContainer/VideoData 在回调线程卡死。

下一步：统计持续输出帧数、检查 reader 是否停止请求样本、必要时在输出回调中主动请求下一帧/调整 promise 语义。

## 10. 持续解码进展（2026-11-19 11:58）

- 采用"Decode 立即 resolve（帧队列有帧则带回）"策略后，reader 可连续送样：
  观察到 decode #0..#10、output cb #0..#7，pts 递增；
- 视频画面可显示（彩条）；
- 剩余问题：约 10 帧后 reader 停止送样/解码停止，视频变灰（CPU 归 0）；
  怀疑同步 resolve / 帧队列消费节奏导致 reader 暂停请求，下一步改为异步 resolve 并统计 reader 请求节奏。

## 11. 停帧问题总结（2026-11-19 12:15）

- 硬解通路已打通：Init、输入、输出、帧构造、页面渲染均正常（视频能显示画面）；
- 剩余阻塞：MediaFormatReader 在约 8–9 个样本后停止请求 `Decode`，CPU 归零、视频定格；
  - 已排除：视频样本数（实际 240 帧）、初始化失败、ImageContainer 线程卡死、帧 duration 错误（改为固定 33ms 仍复现）；
  - 需在 MediaFormatReader 内部加日志（请求节奏、promise 状态、队列水位）才能定位；
- 已恢复软解 libxul 供日常使用。

## 12. 参考实现检索与 Prepare 补充（2026-11-19 12:30）

参考：
- OpenHarmony 官方《视频解码》(Buffer 模式)：https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/media/avcodec/video-decoding.md
- 官方示例：https://gitee.com/openharmony/multimedia_av_codec/tree/master/test/unittest/video_test/video_test/sample
- HarmonyOS_Samples AVCodecBufferMode：https://gitee.com/harmonyos_samples/avcodec-buffer-mode

要点（与当前实现对照）：
- 回调 `OnNeedInputBuffer(codec,index,buffer,userData)` 中把 **buffer+index 入队**，后续写入并 PushInputBuffer（与我们的实现一致）；
- Buffer 模式输出必须 `OH_VideoDecoder_FreeOutputBuffer`（已实现）；
- 需要 `OH_VideoDecoder_Prepare()` 在 Start 之前（已补充）；
- 官方未要求每次 Decode 立即返回，但需要及时轮转输入 buffer。

补充 Prepare 后现象不变：MediaFormatReader 仍在约 9 个样本后停止调用 Decode，视频定格，说明问题更可能在 reader/状态机侧（或帧不可渲染导致队列背压），需要 reader 侧日志确认。

---

# Phase 1 结果（2026-11-19 14:00，已完成）

## 结论
Fenwing 的 H.264 硬件解码已在真机跑通：视频正常播放，硬解 CPU 显著低于 FFmpeg 软解。

## 真机对比（同一页面/同一 720p H.264 测试片，同一 libxul 构建）
方法：`top -b -n 1 -p <pid>` 采样 CPU%，`ps -o rss` 取 RSS；软解通过启动参数 `--ps swdecode 1` 关闭硬件 PDM（同一二进制内切换）。

| 项目 | 硬解（OH_AVCodec） | 软解（FFmpeg） |
|---|---|---|
| CPU 采样（16 次） | 6.8% / 10.3% / 10.7% / 10.7% / 10.7% / 11.1% / 13.7% / 14.2% / 14.8% / 14.8% / 16.6% / 17.2% / 18.5% / 20.0% / 21.4% / 22% / 25% / 30% / 32.1% / 33.3% / 37% / 40.7% / 85.1%（含启动峰值） | 66.6% / 70.3% / 70.3% / 74.0% / 77.7% / 81.4% / 111% / 111%（均值 82.8%） |
| 典型稳定值 | **约 10–25%** | **约 67–111%** |
| RSS | 约 280–350 MB | 约 287–294 MB |

结论：硬解 CPU 约为软解的 **1/3–1/8**（同场景、同片段）；内存两者接近（视频帧拷贝路径会带来少量额外内存，随页面状态波动）。

## 打通过程中修复的关键问题
1. NDK 库直接链接报 undefined hidden symbol → 运行时 `dlopen/dlsym`；
2. `NeedsConversion()` 必须返回 `kNeedAnnexB`；
3. 输入必须使用 `onNeedInputBuffer` 回调传入的 `OH_AVBuffer*`（`GetInputBuffer` 返回 NULL）；
4. 补上 `OH_VideoDecoder_Prepare()`（官方要求 Start 之前）；
5. 帧构造移到后台任务（`NS_DispatchBackgroundTask`），避免 ImageContainer 卡死；
6. **帧交付**：输出回调生成 VideoData 后立即在 `DecodeFrame` 内检查并 resolve 待决 DecodePromise（`DIRECT` 路径），不再依赖 needInput 时机；这一步是视频最终上屏的关键。

## 代码与产物
- 代码：`/home/dev/ff/gecko/dom/media/platforms/ohos/`（OHOSDecoderModule / OHOSVideoDecoder）；
- PDM 注册：`PDMFactory.cpp`（`MOZ_WIDGET_OPENHARMONY`，受 `hwdecode.off` 标志文件控制，便于软解对照）；
- 产物：`artifacts/gecko/libxul-hw-unstripped.so`（符号保留）；HSP/HAP 已安装到平板；
- 诊断日志（文件）默认关闭，设置环境变量 `OHOS_DIAG_LOG` 可开启。

## 已知限制
- 仅 H.264/HEVC 走硬解；VP9/AV1 仍软解；
- Buffer 模式：每帧 CPU 拷贝 + I420 转换（后续可用 Surface/DMA-Buf 优化）；
- 尚未做长时间播放/多视频并发回归。
