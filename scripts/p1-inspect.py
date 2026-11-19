import io
for p in ['/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp','/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp']:
    s=io.open(p,encoding='utf-8').read()
    print('===',p, len(s))
    for kw in ['return decoder','decoder.forget','CreateVideoDecoder','int decNo','needInput resolve','ResolveIfExists']:
        i=s.find(kw)
        print(kw, i)
