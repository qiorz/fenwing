import io

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()

# Add includes
if 'nsThreadUtils.h' not in s:
    s = s.replace('#include "ImageContainer.h"', '#include "ImageContainer.h"\n#include "nsThreadUtils.h"')

start = s.find('void OHOSVideoDecoder::OnNewOutputBuffer(')
assert start > 0
# replace from OnNewOutputBuffer through end of HandleOutput (before closing namespace)
end = s.rfind('}  // namespace mozilla')
assert end > start

new = '''void OHOSVideoDecoder::OnNewOutputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,
                                         OH_AVBuffer* aBuffer, void* aUserData) {
  auto* self = static_cast<OHOSVideoDecoder*>(aUserData);
  if (!self || !self->mCodec || !aBuffer) {
    return;
  }
  OH_AVCodecBufferAttr attr{};
  gApi.bufGetAttr(aBuffer, &attr);
  const int32_t w = self->mSize.width;
  const int32_t h = self->mSize.height;
  if ((attr.flags & AVCODEC_BUFFER_FLAGS_EOS) || w <= 0 || h <= 0) {
    gApi.freeOutput(self->mCodec, aIndex);
    if (attr.flags & AVCODEC_BUFFER_FLAGS_EOS) {
      RefPtr<OHOSVideoDecoder> ref = self;
      NS_DispatchBackgroundTask(NS_NewRunnableFunction(
          "OHOSDecoderEOS", [ref]() { ref->ResolveFrames(); }));
    }
    return;
  }
  uint8_t* addr = gApi.bufAddr(aBuffer);
  if (!addr) {
    gApi.freeOutput(self->mCodec, aIndex);
    return;
  }
  const size_t nv12Size = (size_t)w * h * 3 / 2;
  std::vector<uint8_t> frame(addr, addr + nv12Size);
  gApi.freeOutput(self->mCodec, aIndex);
  static std::atomic<int> sOut{0};
  if (sOut.fetch_add(1) == 0) {
    OHOS_HLOG("first output w=%{public}d h=%{public}d pts=%{public}lld", w, h,
              (long long)attr.pts);
  }
  RefPtr<OHOSVideoDecoder> ref = self;
  const int64_t pts = attr.pts;
  NS_DispatchBackgroundTask(NS_NewRunnableFunction(
      "OHOSDecoderFrame",
      [ref, frame = std::move(frame), w, h, pts]() {
        ref->DecodeFrame(frame, w, h, pts);
      }));
}

void OHOSVideoDecoder::DecodeFrame(const std::vector<uint8_t>& aFrame,
                                   int32_t w, int32_t h, int64_t pts) {
  const size_t ySize = (size_t)w * h;
  const size_t uvSize = (size_t)(w / 2) * (h / 2);
  std::vector<uint8_t> y(ySize), u(uvSize), v(uvSize);
  memcpy(y.data(), aFrame.data(), ySize);
  const uint8_t* uv = aFrame.data() + ySize;
  for (int32_t j = 0; j < h / 2; j++) {
    for (int32_t i = 0; i < w / 2; i++) {
      u[j * (w / 2) + i] = uv[j * w + 2 * i];
      v[j * (w / 2) + i] = uv[j * w + 2 * i + 1];
    }
  }
  VideoData::YCbCrBuffer buffer;
  buffer.mPlanes[0].mData = y.data();
  buffer.mPlanes[0].mWidth = w;
  buffer.mPlanes[0].mHeight = h;
  buffer.mPlanes[0].mStride = w;
  buffer.mPlanes[0].mSkip = 0;
  buffer.mPlanes[1].mData = u.data();
  buffer.mPlanes[1].mWidth = w / 2;
  buffer.mPlanes[1].mHeight = h / 2;
  buffer.mPlanes[1].mStride = w / 2;
  buffer.mPlanes[1].mSkip = 0;
  buffer.mPlanes[2].mData = v.data();
  buffer.mPlanes[2].mWidth = w / 2;
  buffer.mPlanes[2].mHeight = h / 2;
  buffer.mPlanes[2].mStride = w / 2;
  buffer.mPlanes[2].mSkip = 0;
  buffer.mYUVColorSpace = gfx::YUVColorSpace::BT709;
  buffer.mColorDepth = gfx::ColorDepth::COLOR_8;
  buffer.mColorRange = gfx::ColorRange::LIMITED;
  buffer.mChromaSubsampling = gfx::ChromaSubsampling::HALF_WIDTH_AND_HEIGHT;
  auto result = VideoData::CreateAndCopyData(
      mInfo, mImageContainer, 0, media::TimeUnit::FromMicroseconds(pts),
      media::TimeUnit::FromMicroseconds(pts), buffer, true,
      media::TimeUnit::FromMicroseconds(pts), gfx::IntRect(0, 0, w, h),
      nullptr);
  if (result.isErr()) {
    OHOS_HLOG("createAndCopy failed");
    return;
  }
  RefPtr<VideoData> video = result.unwrap();
  if (!video) {
    OHOS_HLOG("video null");
    return;
  }
  MutexAutoLock lock(mMutex);
  mFrames.AppendElement(video);
  DecodedData frames;
  frames.SwapElements(mFrames);
  OHOS_HLOG("resolve frames=%{public}d", (int)frames.Length());
  mDecodePromise.ResolveIfExists(std::move(frames), __func__);
}

void OHOSVideoDecoder::ResolveFrames() {
  MutexAutoLock lock(mMutex);
  DecodedData frames;
  frames.SwapElements(mFrames);
  mDecodePromise.ResolveIfExists(std::move(frames), __func__);
}

'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('background dispatch rewrite done')

# header: add methods and vector/atomic includes
p2 = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.h'
h = io.open(p2, encoding='utf-8').read()
if 'DecodeFrame' not in h:
    h = h.replace('#include "mozilla/Mutex.h"', '#include "mozilla/Mutex.h"\n\n#include <atomic>\n#include <vector>')
    h = h.replace('  void TryPushInput();', '  void TryPushInput();\n  void DecodeFrame(const std::vector<uint8_t>& aFrame, int32_t w, int32_t h,\n                   int64_t pts);\n  void ResolveFrames();')
io.open(p2, 'w', encoding='utf-8').write(h)
print('header updated')
