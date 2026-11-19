import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('  const int64_t frameDur = mInfo.mRate > 0 ? (int64_t)(1000000 / mInfo.mRate) : 33333;',
            '  const int64_t frameDur = 33333;')
io.open(p,'w',encoding='utf-8').write(s)
print('constant duration')
