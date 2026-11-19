import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
old='''  mPendingSample = aSample;
  TryPushInput();
  OHOS_HLOG("decode promise created pending=%{public}d free=%{public}d", mPendingSample ? 1 : 0, (int)mFreeInputs.Length());
  return mDecodePromise.Ensure(__func__);'''
assert s.count(old)==1
new='''  mPendingSample = aSample;
  TryPushInput();
  DecodedData frames;
  frames.SwapElements(mFrames);
  return DecodePromise::CreateAndResolve(std::move(frames), __func__);'''
s=s.replace(old,new)
# remove promise resolve in DecodeFrame/ResolveFrames (frames delivered on next Decode)
s=s.replace('''  OHOS_HLOG("resolve frames=%{public}d", (int)frames.Length());
  mDecodePromise.ResolveIfExists(std::move(frames), __func__);''','''  OHOS_HLOG("queued frames=%{public}d", (int)frames.Length());''')
io.open(p,'w',encoding='utf-8').write(s)
print('decode now resolves immediately')
