import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'prepare = nullptr' not in s:
    s=s.replace('  decltype(&OH_VideoDecoder_Configure) configure = nullptr;',
                '  decltype(&OH_VideoDecoder_Configure) configure = nullptr;\n  decltype(&OH_VideoDecoder_Prepare) prepare = nullptr;')
    s=s.replace('    LOAD_V(configure, "OH_VideoDecoder_Configure");',
                '    LOAD_V(configure, "OH_VideoDecoder_Configure");\n    LOAD_V(prepare, "OH_VideoDecoder_Prepare");')
    s=s.replace('  err = gApi.registerCallback(mCodec, cb, this);\n  if (err == AV_ERR_OK) {\n    OHOS_HLOG("init: start start");',
'''  err = gApi.registerCallback(mCodec, cb, this);
  if (err == AV_ERR_OK) {
    err = gApi.prepare(mCodec);
    OHOS_HLOG("init: prepare done err=%{public}d", (int)err);
  }
  if (err == AV_ERR_OK) {
    OHOS_HLOG("init: start start");''')
io.open(p,'w',encoding='utf-8').write(s)
print('prepare added')
