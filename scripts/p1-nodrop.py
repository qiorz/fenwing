import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
old='''  DecodedData ready;
  ready.SwapElements(self->mFrames);
  if (ready.Length() > 0) {
    OHOS_HLOG("needInput resolve frames=%{public}d", (int)ready.Length());
  }
  self->mDecodePromise.ResolveIfExists(std::move(ready), __func__);'''
assert s.count(old)==1
new='''  if (self->mDecodePromise.Exists()) {
    DecodedData ready;
    ready.SwapElements(self->mFrames);
    OHOS_HLOG("needInput resolve frames=%{public}d", (int)ready.Length());
    self->mDecodePromise.ResolveIfExists(std::move(ready), __func__);
  }'''
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('frames no longer dropped when no promise')
