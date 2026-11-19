import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'hilog/log.h' not in s:
    s=s.replace('#include <dlfcn.h>', '#include <dlfcn.h>\n#include <hilog/log.h>')
    s=s.replace('#define LOG(...) MOZ_LOG(gOHOSDecoderLog, LogLevel::Info, (__VA_ARGS__))',
                '#define LOG(...) MOZ_LOG(gOHOSDecoderLog, LogLevel::Info, (__VA_ARGS__))\n#define LOGH(...) OH_LOG_INFO(LOG_APP, __VA_ARGS__)')
    s=s.replace('  if (!gApi.Load()) {', '  LOGH("OHOSDEC init mime=%{public}s size=%{public}dx%{public}d", mMimeType.get(), (int)mSize.width, (int)mSize.height);\n  if (!gApi.Load()) {\n    LOGH("OHOSDEC dlopen failed");')
    s=s.replace('  mCodec = gApi.createByMime(mMimeType.get());\n  if (!mCodec) {', '  mCodec = gApi.createByMime(mMimeType.get());\n  LOGH("OHOSDEC create codec=%{public}p", (void*)mCodec);\n  if (!mCodec) {')
    s=s.replace('  if (err != AV_ERR_OK) {\n    LOG("configure failed %d", (int)err);', '  if (err != AV_ERR_OK) {\n    LOGH("OHOSDEC configure failed=%{public}d", (int)err);\n    LOG("configure failed %d", (int)err);')
    s=s.replace('  if (err != AV_ERR_OK) {\n    LOG("start failed %d", (int)err);', '  if (err != AV_ERR_OK) {\n    LOGH("OHOSDEC start failed=%{public}d", (int)err);\n    LOG("start failed %d", (int)err);')
    s=s.replace('  mStarted = true;\n  return InitPromise::CreateAndResolve', '  mStarted = true;\n  LOGH("OHOSDEC started ok");\n  return InitPromise::CreateAndResolve')
io.open(p,'w',encoding='utf-8').write(s)

p2='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp'
s2=io.open(p2,encoding='utf-8').read()
if 'hilog/log.h' not in s2:
    s2=s2.replace('#include "OHOSVideoDecoder.h"', '#include <hilog/log.h>\n\n#include "OHOSVideoDecoder.h"')
    s2=s2.replace('  RefPtr<MediaDataDecoder> decoder =', '  OH_LOG_INFO(LOG_APP, "OHOSDEC PDM create mime ok");\n  RefPtr<MediaDataDecoder> decoder =')
io.open(p2,'w',encoding='utf-8').write(s2)
print('hilog instrumentation added')
