import io

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()

start = s.find('RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(')
end = s.find('RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Drain()', start)
assert start > 0 and end > start

new = '''RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(
    MediaRawData* aSample) {
  static std::atomic<int> sDec{0};
  int decNo = sDec.fetch_add(1);
  if (decNo < 40) {
    OHOS_HLOG("decode #%{public}d size=%{public}d", decNo, (int)aSample->Size());
  }
  MutexAutoLock lock(mMutex);
  if (mPendingSample) {
    return DecodePromise::CreateAndReject(
        MediaResult(NS_ERROR_DOM_MEDIA_FATAL_ERR, "pending sample"_ns),
        __func__);
  }
  mPendingSample = aSample;
  TryPushInput();
  RefPtr<DecodePromise::Private> promise = mDecodePromise.Ensure(__func__);
  RefPtr<OHOSVideoDecoder> self = this;
  NS_DispatchBackgroundTask(NS_NewRunnableFunction(
      "OHOSDecoderResolveDecode", [self, promise]() {
        DecodedData frames;
        {
          MutexAutoLock lock(self->mMutex);
          frames.SwapElements(self->mFrames);
        }
        OHOS_HLOG("resolve decode frames=%{public}d", (int)frames.Length());
        promise->Resolve(std::move(frames), __func__);
      }));
  return promise;
}

'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('async decode resolve installed')
