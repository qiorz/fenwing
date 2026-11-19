import io

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.h'
s = io.open(p, encoding='utf-8').read()
if 'mFreeInputs' not in s:
    s = s.replace('  RefPtr<MediaRawData> mPendingSample;',
                  '  RefPtr<MediaRawData> mPendingSample;\n  nsTArray<uint32_t> mFreeInputs;')
    s = s.replace('  void HandleOutput(uint32_t aIndex, OH_AVBuffer* aBuffer);',
                  '  void HandleOutput(uint32_t aIndex, OH_AVBuffer* aBuffer);\n  void TryPushInput();')
io.open(p, 'w', encoding='utf-8').write(s)

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()

start = s.find('void OHOSVideoDecoder::OnNeedInputBuffer(')
end = s.find('RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Drain()', start)
assert start > 0 and end > start

new_block = '''void OHOSVideoDecoder::OnNeedInputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,
                                         OH_AVBuffer* aBuffer, void* aUserData) {
  auto* self = static_cast<OHOSVideoDecoder*>(aUserData);
  if (!self) {
    return;
  }
  MutexAutoLock lock(self->mMutex);
  OHOS_HLOG("needInput idx=%d", (int)aIndex);
  self->mFreeInputs.AppendElement(aIndex);
  self->TryPushInput();
}

void OHOSVideoDecoder::TryPushInput() {
  if (!mCodec) {
    return;
  }
  while (!mFreeInputs.IsEmpty() && (mPendingSample || mEOS)) {
    uint32_t index = mFreeInputs[0];
    mFreeInputs.RemoveElementAt(0);
    OH_AVBuffer* buf = gApi.getInput(mCodec, index);
    if (!buf) {
      continue;
    }
    if (mPendingSample) {
      RefPtr<MediaRawData> sample = std::move(mPendingSample);
      mPendingSample = nullptr;
      uint8_t* addr = gApi.bufAddr(buf);
      int32_t cap = gApi.bufCapacity(buf);
      if (addr && cap > 0 && sample->Size() <= (size_t)cap) {
        memcpy(addr, sample->Data(), sample->Size());
        OH_AVCodecBufferAttr attr{};
        attr.pts = sample->mTime.ToMicroseconds();
        attr.size = (int32_t)sample->Size();
        attr.offset = 0;
        attr.flags = 0;
        gApi.bufSetAttr(buf, &attr);
        OHOS_HLOG("push input size=%d", (int)attr.size);
        gApi.pushInput(mCodec, index);
      }
      return;
    }
    if (mEOS) {
      OH_AVCodecBufferAttr attr{};
      attr.pts = 0;
      attr.size = 0;
      attr.offset = 0;
      attr.flags = AVCODEC_BUFFER_FLAGS_EOS;
      gApi.bufSetAttr(buf, &attr);
      gApi.pushInput(mCodec, index);
      mEOS = false;
      OHOS_HLOG("push eos");
      return;
    }
  }
}

RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(
    MediaRawData* aSample) {
  OHOS_HLOG("decode call size=%d", (int)aSample->Size());
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
  TryPushInput();
  return mDecodePromise.Ensure(__func__);
}

'''
s = s[:start] + new_block + s[end:]
# remove old PushPendingInput stub if present
s = s.replace('void OHOSVideoDecoder::PushPendingInput() {\n  // Input is pulled by OnNeedInputBuffer; nothing to do here.\n}\n\n', '')
io.open(p, 'w', encoding='utf-8').write(s)
print('free-input queue logic installed')
