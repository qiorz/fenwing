import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('\n#include <cstdio>\n}\n','\n')
io.open(p,'w',encoding='utf-8').write(s)
print('stray brace removed')
