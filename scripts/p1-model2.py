import io

p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()

# 1) Decode: no background resolve; ensure promise, push sample.
start = s.find('RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(')
end = s.find('RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Drain()', start)
assert start > 0 and end > start

new = '''RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(
    MediaRawData* aSample) {
  static std::atomic<int> sDec{0};
  int decNo = sDec.fetch_add(1);
  if (decNo < 60) {
    OHOS_HLOG("decode #%{public}d size=%{public}d", decNo, (int)aSample->Size());
  }
  MutexAutoLock lock(mMutex);
  if (mFrames.Length() > 0) {
    DecodedData frames;
    frames.SwapElements(mFrames);
    OHOS_HLOG("decode immediate frames=%{public}d", (int)frames.Length());
    return DecodePromise::CreateAndResolve(std::move(frames), __func__);
  }
  if (mPendingSample) {
    return DecodePromise::CreateAndReject(
        MediaResult(NS_ERROR_DOM_MEDIA_FATAL_ERR, "pending sample"_ns),
        __func__);
  }
  mPendingSample = aSample;
  RefPtr<DecodePromise> promise = mDecodePromise.Ensure(__func__);
  TryPushInput();
  return promise;
}

'''
s = s[:start] + new + s[end:]

# 2) OnNeedInputBuffer: after TryPushInput, resolve pending Decode with queued frames.
s = s.replace('''  self->mFreeInputs.AppendElement(FreeInputBuffer{aIndex, aBuffer});
  self->TryPushInput();
}''',
'''  self->mFreeInputs.AppendElement(FreeInputBuffer{aIndex, aBuffer});
  self->TryPushInput();
  DecodedData ready;
  ready.SwapElements(self->mFrames);
  if (ready.Length() > 0) {
    OHOS_HLOG("needInput resolve frames=%{public}d", (int)ready.Length());
  }
  self->mDecodePromise.ResolveIfExists(std::move(ready), __func__);
}''')

io.open(p, 'w', encoding='utf-8').write(s)
print('input-driven resolve model installed')
