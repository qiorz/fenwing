import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
helper='''
static void OHOSStatGlobal(const char* aTag, int a, int b, int c) {
  char buf[160];
  snprintf(buf, sizeof(buf), "%s a=%d b=%d c=%d", aTag, a, b, c);
  FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
  if (f) { fprintf(f, "%s\\n", buf); fclose(f); }
}
'''
if 'OHOSStatGlobal' not in s:
    a='#include "mozilla/Logging.h"'
    assert s.count(a)==1
    s=s.replace(a, a+'\n#include <cstdio>'+helper)
    s=s.replace('OHOSStat("STAT','OHOSStatGlobal("STAT')
io.open(p,'w',encoding='utf-8').write(s)
print('global stats helper:', 'OHOSStatGlobal' in s)
