import io
# module: log created decoder pointer
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp'
s=io.open(p,encoding='utf-8').read()
if 'CREATE p=' not in s:
    helper='''
#include <cstdio>
static void MPtrTag(const char* aTag, void* p, int a) {
  char buf[128];
  snprintf(buf, sizeof(buf), "%s p=%p a=%d", aTag, p, a);
  FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
  if (f) { fprintf(f, "%s\\n", buf); fclose(f); }
}
'''
    s=s.replace('#include "OHOSVideoDecoder.h"','#include "OHOSVideoDecoder.h"'+helper)
    s=s.replace('  RefPtr<MediaDataDecoder> decoder =','  RefPtr<MediaDataDecoder> decoder =')
    s=s.replace('  return decoder.forget();''','  MPtrTag("CREATE", decoder.get(), 0);\n  return decoder.forget();''')
io.open(p,'w',encoding='utf-8').write(s)
print('module ptr log:', 'CREATE p=' in s)

# decoder: DECODE + RESOLVE tags
p2='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s2=io.open(p2,encoding='utf-8').read()
if 'OHOSPtrTag("DECODE"' not in s2:
    s2=s2.replace('  int decNo = sDec.fetch_add(1);\n  if (decNo < 60) {',
                  '  int decNo = sDec.fetch_add(1);\n  OHOSPtrTag("DECODE", this, decNo, 0);\n  if (decNo < 60) {')
if 'OHOSPtrTag("RESOLVE"' not in s2:
    s2=s2.replace('    OHOS_HLOG("needInput resolve frames=%{public}d", (int)ready.Length());',
                  '    OHOSPtrTag("RESOLVE", self, (int)ready.Length(), 0);\n    OHOS_HLOG("needInput resolve frames=%{public}d", (int)ready.Length());')
io.open(p2,'w',encoding='utf-8').write(s2)
print('decoder tags:', 'OHOSPtrTag("DECODE"' in s2 and 'OHOSPtrTag("RESOLVE"' in s2)
