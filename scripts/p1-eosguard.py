import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
old='''void OHOSVideoDecoder::ResolveFrames() {
  MutexAutoLock lock(mMutex);
  DecodedData frames;
  frames.SwapElements(mFrames);
  mDecodePromise.ResolveIfExists(std::move(frames), __func__);
}'''
assert s.count(old)==1
new='''void OHOSVideoDecoder::ResolveFrames() {
  MutexAutoLock lock(mMutex);
  if (mDecodePromise.IsEmpty()) {
    OHOSPtrTag("EOS_NO_PROMISE", this, (int)mFrames.Length(), 0);
    return;
  }
  DecodedData frames;
  frames.SwapElements(mFrames);
  OHOSPtrTag("EOS_RESOLVE", this, (int)frames.Length(), 0);
  mDecodePromise.ResolveIfExists(std::move(frames), __func__);
}'''
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('ResolveFrames guarded')
