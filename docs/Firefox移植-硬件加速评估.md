# Fenwing / Gecko for HarmonyOS —— GPU 与硬件解码评估（2026-11-18）

## 一、GPU 加速：**已启用**

引擎日志（真机）：

```
[WR_EGL] RenderCompositorEGL::Create 进入, kIsOHOS=1
[WR_EGL] UseEGL()=true, 获取 SingletonGL
[WR_EGL] partial present 能力探测: 1 (KHR_partial_update)
[WR_OGL] UpdateAndRender #1 beginFrame=1 present=1
```

结论：
- 走 **WebRender + RenderCompositorEGL**（OpenGL ES）路径，即 GPU 合成与栅格化已开启；
- 支持 `KHR_partial_update`（局部刷新，省电/降带宽）；
- 没有回退到软件 WebRender（日志中无 SWGL 路径）。

## 二、硬件视频解码：**当前未启用**

- 代码检索：`OH_AVCodec` / `OH_AVCodecBase` 在 Gecko 与移植层中**没有任何调用**；
- 媒体解码依赖 `gkcodecs` / `mozavcodec`（FFmpeg 软件解码）；
- 因此 H.264/HEVC 视频目前是 **CPU 软解**，功耗与高分辨率性能有优化空间。

## 三、设备能力（OH_AVCodec Capability API 实测）

通过新增 NAPI `codecProbe()`（`OH_AVCodec_GetCapabilityList`）在真机枚举：

| 解码器 | MIME | 硬件 | 最大实例 |
|---|---|---|---|
| OMX.hisi.video.decoder.avc | video/avc (H.264) | ✅ | 30 |
| OMX.hisi.video.decoder.hevc | video/hevc (H.265) | ✅ | 30 |
| ...hevc.secure / avc.secure | 安全解码 | ✅ | 2 |
| OH.Media.Codec.Decoder.Video.VP8 | video/vp8 | ❌ 软件 | 64 |
| OH.Media.Codec.Decoder.Video.VP9 | video/vp9 | ❌ 软件 | 64 |
| OH.Media.Codec.Decoder.Video.AV1 | video/av1 | ❌ 软件 | 64 |
| OH.Media.Codec.Decoder.Video.AVC/HEVC | 软件兜底 | ❌ | 64 |
| MPEG2/MPEG4/MPEG/H263/MSVIDEO1 | 软件 | ❌ | 64 |

结论：设备对 **H.264 / HEVC 有硬件解码器**（海思 OMX，30 路实例），VP8/VP9/AV1 只有软件解码。

## 四、接入硬件解码的方案（建议）

Gecko 侧需要新增 `OHOSPlatformDecoderModule`（类似 Android 的 `AndroidDecoderModule`）：

1. **Phase 1（建议先做，1–2 周）**
   - 用 `OH_VideoDecoder_*`（native_avcodec_video_decoder.h）创建 H.264/HEVC 解码器；
   - 输出用 ByteBuffer（NV12/I420），封装为 Gecko `VideoData` 交给现有渲染管线；
   - 优点：纯 CPU 侧零拷贝之外的改动小；H.264/HEVC 硬解生效，CPU 大幅下降；
   - 注意：颜色空间/stride 对齐、错误恢复、seek flush。

2. **Phase 2（进阶，2–4 周）**
   - Surface 输出 + DMABuf → WebRender external image（真正零拷贝）；
   - 需要 OHOS 的 native window / GraphicBuffer 与 WR 的外部纹理桥接，复杂度高。

3. **接入点**
   - `media/ffvpx`、`gkcodecs` 保持软件兜底（VP9/AV1 仍走软解）；
   - PDMFactory 注册 OHOS 解码器，优先 HW，失败回退 FFmpeg。

## 五、本轮落地内容

- 新增 NAPI `codecProbe()`（`libgecko_napi`，链接 `libnative_media_codecbase.so`）；
- 启动时把设备解码器能力打到 hilog（`video decoders: [...]`），可用于后续 PDM 决策与问题定位；
- 未修改解码路径（避免未验证的半成品影响播放）。

## 六、建议下一步

1. 先做 Phase 1（H.264/HEVC ByteBuffer 硬解），用视频站点验证 CPU 占用/掉帧；
2. 同时可在设置里增加"解码器信息"展示（当前仅在日志）；
3. GPU 侧已无阻塞；后续可评估 `gfx.webrender.*` 高级特性（如 GPU 画布加速）是否值得开启。
