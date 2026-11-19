import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('#include <hilog/log.h>\n','')
s=s.replace('#define LOGH(...) OH_LOG_INFO(LOG_APP, __VA_ARGS__)',
'''#include <cstdio>
static void OHOSMarker(const char* aMsg) {
  FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
  if (f) {
    fprintf(f, "%s\\n", aMsg);
    fclose(f);
  }
}''')
s=s.replace('LOGH("OHOSDEC init mime=%{public}s size=%{public}dx%{public}d", mMimeType.get(), (int)mSize.width, (int)mSize.height);',
            'OHOSMarker("OHOSDEC init");')
s=s.replace('LOGH("OHOSDEC dlopen failed");','OHOSMarker("OHOSDEC dlopen failed");')
s=s.replace('LOGH("OHOSDEC create codec=%{public}p", (void*)mCodec);','OHOSMarker("OHOSDEC create codec");')
s=s.replace('LOGH("OHOSDEC configure failed=%{public}d", (int)err);','OHOSMarker("OHOSDEC configure failed");')
s=s.replace('LOGH("OHOSDEC start failed=%{public}d", (int)err);','OHOSMarker("OHOSDEC start failed");')
s=s.replace('LOGH("OHOSDEC started ok");','OHOSMarker("OHOSDEC started ok");')
io.open(p,'w',encoding='utf-8').write(s)
p2='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp'
s2=io.open(p2,encoding='utf-8').read()
s2=s2.replace('#include <hilog/log.h>\n\n','')
s2=s2.replace('  OH_LOG_INFO(LOG_APP, "OHOSDEC PDM create mime ok");\n','')
io.open(p2,'w',encoding='utf-8').write(s2)
print('file markers added')
