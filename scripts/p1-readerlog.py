import io
p='/home/dev/ff/gecko/dom/media/MediaFormatReader.cpp'
s=io.open(p,encoding='utf-8',errors='replace').read()
if 'READERLOG' not in s:
    helper='''
#include <cstdio>
static void READERLOG(const char* aFmt, ...) {
  char buf[192];
  va_list ap; va_start(ap, aFmt);
  vsnprintf(buf, sizeof(buf), aFmt, ap);
  va_end(ap);
  FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
  if (f) { fprintf(f, "%s\\n", buf); fclose(f); }
}
'''
    a='#include "MediaFormatReader.h"'
    idx=s.find(a)
    assert idx>0
    s=s[:idx+len(a)]+helper+s[idx+len(a):]
    target='void MediaFormatReader::NotifyNewOutput('
    idx=s.find(target)
    assert idx>0
    brace=s.find('{', idx)+1
    s=s[:brace]+'''
  READERLOG("READER output n=%d pts0=%lld", (int)aResults.Length(),
            aResults.IsEmpty() ? -1 : (long long)aResults[0]->mTime.ToMicroseconds());
'''+s[brace:]
io.open(p,'w',encoding='utf-8').write(s)
print('reader log added:', 'READERLOG' in s)
