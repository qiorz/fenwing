import io

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()

start = s.find('  uint8_t* addr = gApi.bufAddr(aBuffer);')
end = s.find('  MutexAutoLock lock(mMutex);\n  mFrames.AppendElement(video);', start)
assert start > 0 and end > start

new = '''  uint8_t* addr = gApi.bufAddr(aBuffer);
  const int32_t w = mSize.width;
  const int32_t h = mSize.height;
  if (!addr || w <= 0 || h <= 0 || !mImageContainer) {
    gApi.freeOutput(mCodec, aIndex);
    return;
  }
  const size_t ySize = (size_t)w * h;
  const size_t uvSize = (size_t)(w / 2) * (h / 2);
  auto yPlane = MakeUnique<uint8_t[]>(ySize);
  auto uPlane = MakeUnique<uint8_t[]>(uvSize);
  auto vPlane = MakeUnique<uint8_t[]>(uvSize);
  if (!yPlane || !uPlane || !vPlane) {
    gApi.freeOutput(mCodec, aIndex);
    return;
  }
  memcpy(yPlane.get(), addr, ySize);
  const uint8_t* uv = addr + ySize;
  for (int32_t j = 0; j < h / 2; j++) {
    for (int32_t i = 0; i < w / 2; i++) {
      uPlane[j * (w / 2) + i] = uv[j * w + 2 * i];
      vPlane[j * (w / 2) + i] = uv[j * w + 2 * i + 1];
    }
  }
  gApi.freeOutput(mCodec, aIndex);

  VideoData::YCbCrBuffer buffer;
  buffer.mPlanes[0].mData = yPlane.get();
  buffer.mPlanes[0].mWidth = w;
  buffer.mPlanes[0].mHeight = h;
  buffer.mPlanes[0].mStride = w;
  buffer.mPlanes[0].mSkip = 0;
  buffer.mPlanes[1].mData = uPlane.get();
  buffer.mPlanes[1].mWidth = w / 2;
  buffer.mPlanes[1].mHeight = h / 2;
  buffer.mPlanes[1].mStride = w / 2;
  buffer.mPlanes[1].mSkip = 0;
  buffer.mPlanes[2].mData = vPlane.get();
  buffer.mPlanes[2].mWidth = w / 2;
  buffer.mPlanes[2].mHeight = h / 2;
  buffer.mPlanes[2].mStride = w / 2;
  buffer.mPlanes[2].mSkip = 0;
  buffer.mYUVColorSpace = gfx::YUVColorSpace::BT709;
  buffer.mColorDepth = gfx::ColorDepth::COLOR_8;
  buffer.mColorRange = gfx::ColorRange::LIMITED;
  buffer.mChromaSubsampling = gfx::ChromaSubsampling::HALF_WIDTH_AND_HEIGHT;

  auto result = VideoData::CreateAndCopyData(
      mInfo, mImageContainer, 0, media::TimeUnit::FromMicroseconds(attr.pts),
      media::TimeUnit::FromMicroseconds(attr.pts), buffer, true,
      media::TimeUnit::FromMicroseconds(attr.pts), gfx::IntRect(0, 0, w, h),
      nullptr);
  if (result.isErr()) {
    return;
  }
  RefPtr<VideoData> video = result.unwrap();
  if (!video) {
    return;
  }
'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('I420 conversion path installed')
