import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp'
s=io.open(p,encoding='utf-8').read()
if 'OHOSMarker' not in s:
    s=s.replace('#include "OHOSDecoderModule.h"',
'''#include "OHOSDecoderModule.h"

#include <cstdio>
static void OHOSMarker(const char* aMsg) {
  FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
  if (f) {
    fprintf(f, "%s\\n", aMsg);
    fclose(f);
  }
}''')
    s=s.replace('already_AddRefed<PlatformDecoderModule> OHOSDecoderModule::Create() {',
                'already_AddRefed<PlatformDecoderModule> OHOSDecoderModule::Create() {\n  OHOSMarker("OHOSDEC module Create");')
    s=s.replace('already_AddRefed<MediaDataDecoder> OHOSDecoderModule::CreateVideoDecoder(',
                'already_AddRefed<MediaDataDecoder> OHOSDecoderModule::CreateVideoDecoder(')
    s=s.replace('  const TrackInfo& info = aParams.mConfig;', '  OHOSMarker("OHOSDEC CreateVideoDecoder called");\n  const TrackInfo& info = aParams.mConfig;')
io.open(p,'w',encoding='utf-8').write(s)
print('module markers added')
