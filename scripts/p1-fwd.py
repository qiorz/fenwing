import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'static void OHOSMarker(const char* aMsg);' not in s:
    s=s.replace('static void OHOSStat(', 'static void OHOSMarker(const char* aMsg);\nstatic void OHOSStat(')
io.open(p,'w',encoding='utf-8').write(s)
print('forward decl added')
