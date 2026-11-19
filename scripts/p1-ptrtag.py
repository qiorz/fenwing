import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'PTRTAG' not in s:
    helper='''
static void OHOSPtrTag(const char* aTag, void* p, int a, int b) {
  char buf[160];
  snprintf(buf, sizeof(buf), "%s p=%p a=%d b=%d", aTag, p, a, b);
  FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
  if (f) { fprintf(f, "%s\\n", buf); fclose(f); }
}
'''
    a='#include "mozilla/Logging.h"'
    s=s.replace(a, a+'\n#include <cstdio>'+helper,1)
    s=s.replace('  OHOSMarker("QUEUED");',
                '  OHOSPtrTag("QUEUED", this, (int)mFrames.Length(), 0);')
    s=s.replace('  int decNo = sDec.fetch_add(1);\n  if (decNo < 60) {',
                '  int decNo = sDec.fetch_add(1);\n  OHOSPtrTag("DECODE", this, decNo, (int)mFrames.Length());\n  if (decNo < 60) {')
    s=s.replace('void OHOSVideoDecoder::OnNewOutputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,\n                                         OH_AVBuffer* aBuffer, void* aUserData) {\n  auto* self = static_cast<OHOSVideoDecoder*>(aUserData);\n  if (!self || !self->mCodec || !aBuffer) {',
                'void OHOSVideoDecoder::OnNewOutputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,\n                                         OH_AVBuffer* aBuffer, void* aUserData) {\n  auto* self = static_cast<OHOSVideoDecoder*>(aUserData);\n  if (!self || !self->mCodec || !aBuffer) {\n    return;\n  }\n  { static int s0 = 0; if (s0++ < 3) { OHOSPtrTag("OUTPUT", self, (int)aIndex, 0); } }')
io.open(p,'w',encoding='utf-8').write(s)
print('ptr tags:', 'PTRTAG' in s or 'OHOSPtrTag' in s)
