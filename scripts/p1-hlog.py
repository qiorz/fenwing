import io

# Add dlopen-based hilog logging so markers survive a frozen UI thread.
p = '/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()

if 'OHOS_HLOG' not in s:
    helper = '''
#define OHOS_HLOG(...)                                       \\
  do {                                                       \\
    typedef int (*OhLogPrintFn)(int, int, unsigned int,      \\
                                const char*, const char*, ...); \\
    static void* sHilog = dlopen("libhilog_ndk.z.so", RTLD_NOW); \\
    static OhLogPrintFn sPrint =                             \\
        sHilog ? (OhLogPrintFn)dlsym(sHilog, "OH_LOG_Print") : nullptr; \\
    if (sPrint) {                                            \\
      sPrint(0, 4, 0, "OHOSDEC", __VA_ARGS__);               \\
    }                                                        \\
  } while (0)
'''
    s = s.replace('#define OHOSMarker', helper + '\n#define OHOSMarker', 1) if '#define OHOSMarker' in s else s.replace('#define LOG(...) MOZ_LOG(gOHOSDecoderLog, LogLevel::Info, (__VA_ARGS__))', '#define LOG(...) MOZ_LOG(gOHOSDecoderLog, LogLevel::Info, (__VA_ARGS__))' + helper, 1)

    # step markers in Init
    s = s.replace('  mCodec = gApi.createByMime(mMimeType.get());',
                  '  OHOS_HLOG("init: createByMime start");\n  mCodec = gApi.createByMime(mMimeType.get());\n  OHOS_HLOG("init: createByMime done");')
    s = s.replace('  OH_AVFormat* format = gApi.fmtCreate();',
                  '  OHOS_HLOG("init: configure start");\n  OH_AVFormat* format = gApi.fmtCreate();')
    s = s.replace('  OH_AVErrCode err = gApi.configure(mCodec, format);',
                  '  OH_AVErrCode err = gApi.configure(mCodec, format);\n  OHOS_HLOG("init: configure done");')
    s = s.replace('  err = gApi.registerCallback(mCodec, cb, this);',
                  '  OHOS_HLOG("init: registerCallback start");\n  err = gApi.registerCallback(mCodec, cb, this);\n  OHOS_HLOG("init: registerCallback done");')
    s = s.replace('  if (err == AV_ERR_OK) {\n    err = gApi.start(mCodec);\n  }',
                  '  if (err == AV_ERR_OK) {\n    OHOS_HLOG("init: start start");\n    err = gApi.start(mCodec);\n    OHOS_HLOG("init: start done");\n  }')
    s = s.replace('  mStarted = true;', '  mStarted = true;\n  OHOS_HLOG("init: ready");')
io.open(p, 'w', encoding='utf-8').write(s)
print('hilog markers added:', 'OHOS_HLOG' in s)
