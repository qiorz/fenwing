import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'resolve frames' not in s:
    s=s.replace('  mPendingSample = aSample;\n  TryPushInput();\n  return mDecodePromise.Ensure(__func__);',
'''  mPendingSample = aSample;
  TryPushInput();
  OHOS_HLOG("decode promise created pending=%{public}d", mPendingSample ? 1 : 0);
  return mDecodePromise.Ensure(__func__);''')
    s=s.replace('  if (sOutCount == 0) { OHOS_HLOG("first output w=%d h=%d", w, h); }',
                '  if (sOutCount == 0) { OHOS_HLOG("first output w=%{public}d h=%{public}d pts=%{public}lld", w, h, (long long)attr.pts); }')
    s=s.replace('  mFrames.AppendElement(video);\n  DecodedData frames;\n  frames.SwapElements(mFrames);\n  mDecodePromise.ResolveIfExists(std::move(frames), __func__);',
'''  mFrames.AppendElement(video);
  DecodedData frames;
  frames.SwapElements(mFrames);
  OHOS_HLOG("resolve frames=%{public}d pts=%{public}lld", (int)frames.Length(), (long long)attr.pts);
  mDecodePromise.ResolveIfExists(std::move(frames), __func__);''')
io.open(p,'w',encoding='utf-8').write(s)
print('resolve markers added:', 'resolve frames' in s)
