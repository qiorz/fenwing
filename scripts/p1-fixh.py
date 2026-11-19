import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
old='''  const int32_t w = mSize.width;
  if (sOutCount == 0) { OHOS_HLOG("first output w=%d h=%d", w, h); }
  sOutCount++;
  if (sOutCount % 30 == 1) { OHOS_HLOG("output #%d", sOutCount); }
  const int32_t h = mSize.height;'''
assert s.count(old)==1
new='''  const int32_t w = mSize.width;
  const int32_t h = mSize.height;
  if (sOutCount == 0) { OHOS_HLOG("first output w=%d h=%d", w, h); }
  sOutCount++;
  if (sOutCount % 30 == 1) { OHOS_HLOG("output #%d", sOutCount); }'''
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('fixed h order')
