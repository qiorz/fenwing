/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "OHOSVideoDecoder.h"

#include <dlfcn.h>

#include <multimedia/player_framework/native_avbuffer.h>
#include <multimedia/player_framework/native_avformat.h>

#include "ImageContainer.h"
#include "VideoUtils.h"
#include "mozilla/Logging.h"

namespace mozilla {

LazyLogModule gOHOSDecoderLog("OHOSDecoder");
#define LOG(...) MOZ_LOG(gOHOSDecoderLog, LogLevel::Info, (__VA_ARGS__))

namespace {

// The OHOS NDK codec libraries are loaded at runtime: linking libxul against
// the NDK stubs fails with "undefined hidden symbol" for these entry points.
struct OhosCodecApi {
  void* vdec = nullptr;
  void* core = nullptr;

  decltype(&OH_VideoDecoder_CreateByMime) createByMime = nullptr;
  decltype(&OH_VideoDecoder_Destroy) destroy = nullptr;
  decltype(&OH_VideoDecoder_Configure) configure = nullptr;
  decltype(&OH_VideoDecoder_RegisterCallback) registerCallback = nullptr;
  decltype(&OH_VideoDecoder_Start) start = nullptr;
  decltype(&OH_VideoDecoder_Stop) stop = nullptr;
  decltype(&OH_VideoDecoder_Flush) flush = nullptr;
  decltype(&OH_VideoDecoder_PushInputBuffer) pushInput = nullptr;
  decltype(&OH_VideoDecoder_FreeOutputBuffer) freeOutput = nullptr;
  decltype(&OH_VideoDecoder_GetInputBuffer) getInput = nullptr;
  decltype(&OH_VideoDecoder_GetOutputBuffer) getOutput = nullptr;
  decltype(&OH_AVBuffer_GetAddr) bufAddr = nullptr;
  decltype(&OH_AVBuffer_GetCapacity) bufCapacity = nullptr;
  decltype(&OH_AVBuffer_GetBufferAttr) bufGetAttr = nullptr;
  decltype(&OH_AVBuffer_SetBufferAttr) bufSetAttr = nullptr;
  decltype(&OH_AVFormat_Create) fmtCreate = nullptr;
  decltype(&OH_AVFormat_SetIntValue) fmtSetInt = nullptr;
  decltype(&OH_AVFormat_Destroy) fmtDestroy = nullptr;

  const char* keyWidth = "width";
  const char* keyHeight = "height";
  const char* keyPixelFormat = "pixel_format";

  bool Load() {
    if (createByMime) {
      return true;
    }
    vdec = dlopen("libnative_media_vdec.so", RTLD_NOW | RTLD_GLOBAL);
    core = dlopen("libnative_media_core.so", RTLD_NOW | RTLD_GLOBAL);
    if (!vdec || !core) {
      LOG("dlopen codec failed: %s", dlerror());
      return false;
    }
#define LOAD_V(field, name)                              \
  field = reinterpret_cast<decltype(field)>(dlsym(vdec, name)); \
  if (!field) {                                          \
    LOG("missing symbol %s", name);                      \
    return false;                                        \
  }
#define LOAD_C(field, name)                              \
  field = reinterpret_cast<decltype(field)>(dlsym(core, name)); \
  if (!field) {                                          \
    LOG("missing symbol %s", name);                      \
    return false;                                        \
  }
    LOAD_V(createByMime, "OH_VideoDecoder_CreateByMime");
    LOAD_V(destroy, "OH_VideoDecoder_Destroy");
    LOAD_V(configure, "OH_VideoDecoder_Configure");
    LOAD_V(registerCallback, "OH_VideoDecoder_RegisterCallback");
    LOAD_V(start, "OH_VideoDecoder_Start");
    LOAD_V(stop, "OH_VideoDecoder_Stop");
    LOAD_V(flush, "OH_VideoDecoder_Flush");
    LOAD_V(pushInput, "OH_VideoDecoder_PushInputBuffer");
    LOAD_V(freeOutput, "OH_VideoDecoder_FreeOutputBuffer");
    LOAD_V(getInput, "OH_VideoDecoder_GetInputBuffer");
    LOAD_V(getOutput, "OH_VideoDecoder_GetOutputBuffer");
    LOAD_C(bufAddr, "OH_AVBuffer_GetAddr");
    LOAD_C(bufCapacity, "OH_AVBuffer_GetCapacity");
    LOAD_C(bufGetAttr, "OH_AVBuffer_GetBufferAttr");
    LOAD_C(bufSetAttr, "OH_AVBuffer_SetBufferAttr");
    LOAD_C(fmtCreate, "OH_AVFormat_Create");
    LOAD_C(fmtSetInt, "OH_AVFormat_SetIntValue");
    LOAD_C(fmtDestroy, "OH_AVFormat_Destroy");
#undef LOAD_V
#undef LOAD_C
    return true;
  }
};

OhosCodecApi gApi;

}  // namespace

OHOSVideoDecoder::OHOSVideoDecoder(const CreateDecoderParams& aParams,
                                   const nsACString& aMime)
    : mInfo(aParams.VideoConfig()),
      mMimeType(aMime),
      mImageContainer(aParams.mImageContainer),
      mMutex("OHOSVideoDecoder") {
  mSize = mInfo.mDisplay;
  if (mSize.width <= 0 || mSize.height <= 0) {
    mSize = gfx::IntSize(640, 360);
  }
}

RefPtr<MediaDataDecoder::InitPromise> OHOSVideoDecoder::Init() {
  if (!gApi.Load()) {
    return InitPromise::CreateAndReject(
        MediaResult(NS_ERROR_DOM_MEDIA_NOT_SUPPORTED_ERR, "no OH_AVCodec"_ns),
        __func__);
  }
  mCodec = gApi.createByMime(mMimeType.get());
  if (!mCodec) {
    return InitPromise::CreateAndReject(
        MediaResult(NS_ERROR_DOM_MEDIA_NOT_SUPPORTED_ERR, "no codec"_ns),
        __func__);
  }
  OH_AVFormat* format = gApi.fmtCreate();
  gApi.fmtSetInt(format, gApi.keyWidth, mSize.width);
  gApi.fmtSetInt(format, gApi.keyHeight, mSize.height);
  gApi.fmtSetInt(format, gApi.keyPixelFormat, AV_PIXEL_FORMAT_NV12);
  OH_AVErrCode err = gApi.configure(mCodec, format);
  gApi.fmtDestroy(format);
  if (err != AV_ERR_OK) {
    LOG("configure failed %d", (int)err);
    gApi.destroy(mCodec);
    mCodec = nullptr;
    return InitPromise::CreateAndReject(
        MediaResult(NS_ERROR_DOM_MEDIA_FATAL_ERR, "configure failed"_ns),
        __func__);
  }
  OH_AVCodecCallback cb{};
  cb.onError = &OHOSVideoDecoder::OnError;
  cb.onStreamChanged = &OHOSVideoDecoder::OnStreamChanged;
  cb.onNeedInputBuffer = &OHOSVideoDecoder::OnNeedInputBuffer;
  cb.onNewOutputBuffer = &OHOSVideoDecoder::OnNewOutputBuffer;
  err = gApi.registerCallback(mCodec, cb, this);
  if (err == AV_ERR_OK) {
    err = gApi.start(mCodec);
  }
  if (err != AV_ERR_OK) {
    LOG("start failed %d", (int)err);
    gApi.destroy(mCodec);
    mCodec = nullptr;
    return InitPromise::CreateAndReject(
        MediaResult(NS_ERROR_DOM_MEDIA_FATAL_ERR, "start failed"_ns), __func__);
  }
  mStarted = true;
  return InitPromise::CreateAndResolve(TrackInfo::kVideoTrack, __func__);
}

void OHOSVideoDecoder::OnError(OH_AVCodec*, int32_t aErrorCode, void* aUserData) {
  auto* self = static_cast<OHOSVideoDecoder*>(aUserData);
  LOG("codec error %d", (int)aErrorCode);
  if (self) {
    MutexAutoLock lock(self->mMutex);
    self->mDecodePromise.RejectIfExists(
        MediaResult(NS_ERROR_DOM_MEDIA_FATAL_ERR, "OHOS decoder error"_ns),
        __func__);
  }
}

void OHOSVideoDecoder::OnStreamChanged(OH_AVCodec*, OH_AVFormat*, void*) {}

void OHOSVideoDecoder::OnNeedInputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,
                                         OH_AVBuffer* aBuffer, void* aUserData) {
  auto* self = static_cast<OHOSVideoDecoder*>(aUserData);
  if (!self || !aBuffer) {
    return;
  }
  MutexAutoLock lock(self->mMutex);
  if (self->mPendingSample) {
    RefPtr<MediaRawData> sample = std::move(self->mPendingSample);
    uint8_t* addr = gApi.bufAddr(aBuffer);
    int32_t cap = gApi.bufCapacity(aBuffer);
    if (addr && cap > 0 && sample->Size() <= (size_t)cap) {
      memcpy(addr, sample->Data(), sample->Size());
      OH_AVCodecBufferAttr attr{};
      attr.pts = sample->mTime.ToMicroseconds();
      attr.size = (int32_t)sample->Size();
      attr.offset = 0;
      attr.flags = 0;
      gApi.bufSetAttr(aBuffer, &attr);
      gApi.pushInput(aCodec, aIndex);
      return;
    }
  }
  if (self->mEOS) {
    OH_AVCodecBufferAttr attr{};
    attr.pts = 0;
    attr.size = 0;
    attr.offset = 0;
    attr.flags = AVCODEC_BUFFER_FLAGS_EOS;
    gApi.bufSetAttr(aBuffer, &attr);
    gApi.pushInput(aCodec, aIndex);
    self->mEOS = false;
  }
}

RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(
    MediaRawData* aSample) {
  MutexAutoLock lock(mMutex);
  if (mFrames.Length() > 0) {
    DecodedData frames;
    frames.SwapElements(mFrames);
    return DecodePromise::CreateAndResolve(std::move(frames), __func__);
  }
  if (mPendingSample) {
    return DecodePromise::CreateAndReject(
        MediaResult(NS_ERROR_DOM_MEDIA_FATAL_ERR, "pending sample"_ns),
        __func__);
  }
  mPendingSample = aSample;
  return mDecodePromise.Ensure(__func__);
}

RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Drain() {
  MutexAutoLock lock(mMutex);
  mEOS = true;
  DecodedData frames;
  frames.SwapElements(mFrames);
  return DecodePromise::CreateAndResolve(std::move(frames), __func__);
}

RefPtr<MediaDataDecoder::FlushPromise> OHOSVideoDecoder::Flush() {
  MutexAutoLock lock(mMutex);
  mPendingSample = nullptr;
  mEOS = false;
  mFrames.Clear();
  mDecodePromise.RejectIfExists(
      MediaResult(NS_ERROR_DOM_MEDIA_CANCELED, "flush"_ns), __func__);
  if (mCodec) {
    gApi.flush(mCodec);
  }
  return FlushPromise::CreateAndResolve(true, __func__);
}

RefPtr<ShutdownPromise> OHOSVideoDecoder::Shutdown() {
  MutexAutoLock lock(mMutex);
  mShutdown = true;
  mPendingSample = nullptr;
  mDecodePromise.RejectIfExists(
      MediaResult(NS_ERROR_DOM_MEDIA_CANCELED, "shutdown"_ns), __func__);
  if (mCodec) {
    if (mStarted) {
      gApi.stop(mCodec);
    }
    gApi.destroy(mCodec);
    mCodec = nullptr;
  }
  return ShutdownPromise::CreateAndResolve(true, __func__);
}

void OHOSVideoDecoder::OnNewOutputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,
                                         OH_AVBuffer* aBuffer, void* aUserData) {
  auto* self = static_cast<OHOSVideoDecoder*>(aUserData);
  if (!self || !self->mCodec) {
    return;
  }
  self->HandleOutput(aIndex, aBuffer);
}

void OHOSVideoDecoder::HandleOutput(uint32_t aIndex, OH_AVBuffer* aBuffer) {
  if (!aBuffer) {
    gApi.freeOutput(mCodec, aIndex);
    return;
  }
  OH_AVCodecBufferAttr attr{};
  gApi.bufGetAttr(aBuffer, &attr);
  if (attr.flags & AVCODEC_BUFFER_FLAGS_EOS) {
    gApi.freeOutput(mCodec, aIndex);
    MutexAutoLock lock(mMutex);
    DecodedData frames;
    frames.SwapElements(mFrames);
    mDecodePromise.ResolveIfExists(std::move(frames), __func__);
    return;
  }
  uint8_t* addr = gApi.bufAddr(aBuffer);
  const int32_t w = mSize.width;
  const int32_t h = mSize.height;
  if (!addr || w <= 0 || h <= 0 || !mImageContainer) {
    gApi.freeOutput(mCodec, aIndex);
    return;
  }
  RefPtr<layers::Image> image = mImageContainer->CreatePlanarYCbCrImage();
  if (!image) {
    gApi.freeOutput(mCodec, aIndex);
    return;
  }
  auto* yuv = image->AsPlanarYCbCrImage();
  layers::PlanarYCbCrData data;
  data.mYChannel = addr;
  data.mYStride = w;
  data.mCbChannel = addr + (w * h);
  data.mCrChannel = nullptr;
  data.mCbCrStride = w;
  data.mPictureRect = gfx::IntRect(0, 0, w, h);
  data.mChromaSubsampling = gfx::ChromaSubsampling::HALF_WIDTH_AND_HEIGHT;
  data.mColorDepth = gfx::ColorDepth::COLOR_8;
  data.mYUVColorSpace = gfx::YUVColorSpace::BT709;
  data.mColorRange = gfx::ColorRange::LIMITED;
  if (NS_FAILED(yuv->CopyData(data))) {
    gApi.freeOutput(mCodec, aIndex);
    return;
  }
  gApi.freeOutput(mCodec, aIndex);
  RefPtr<VideoData> video = VideoData::CreateFromImage(
      mSize, 0, media::TimeUnit::FromMicroseconds(attr.pts),
      media::TimeUnit::FromMicroseconds(attr.pts), image, true,
      media::TimeUnit::FromMicroseconds(attr.pts));
  if (!video) {
    return;
  }
  MutexAutoLock lock(mMutex);
  mFrames.AppendElement(video);
  DecodedData frames;
  frames.SwapElements(mFrames);
  mDecodePromise.ResolveIfExists(std::move(frames), __func__);
}

}  // namespace mozilla
