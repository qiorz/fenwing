import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
old='''  mFrames.AppendElement(video);
  OHOSPtrTag("QUEUED", this, (int)mFrames.Length(), 0);'''
assert s.count(old)==1
new='''  mFrames.AppendElement(video);
  OHOSPtrTag("QUEUED", this, (int)mFrames.Length(), 0);
  if (!mDecodePromise.IsEmpty()) {
    DecodedData ready;
    ready.SwapElements(mFrames);
    OHOSPtrTag("DIRECT", this, (int)ready.Length(), 0);
    mDecodePromise.ResolveIfExists(std::move(ready), __func__);
  }'''
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('direct delivery installed')
