import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('''  RefPtr<DecodePromise::Private> promise = mDecodePromise.Ensure(__func__);
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
  return promise;''',
'''  RefPtr<DecodePromise> promise = mDecodePromise.Ensure(__func__);
  RefPtr<OHOSVideoDecoder> self = this;
  NS_DispatchBackgroundTask(NS_NewRunnableFunction(
      "OHOSDecoderResolveDecode", [self]() {
        DecodedData frames;
        {
          MutexAutoLock lock(self->mMutex);
          frames.SwapElements(self->mFrames);
        }
        OHOS_HLOG("resolve decode frames=%{public}d", (int)frames.Length());
        self->mDecodePromise.ResolveIfExists(std::move(frames), __func__);
      }));
  return promise;''')
io.open(p,'w',encoding='utf-8').write(s)
print('holder-based async resolve')
