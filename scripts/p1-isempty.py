import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('  if (self->mDecodePromise.Exists()) {','  if (!self->mDecodePromise.IsEmpty()) {')
io.open(p,'w',encoding='utf-8').write(s)
print('using IsEmpty')
