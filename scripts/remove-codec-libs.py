import io
p='/home/dev/ff/gecko/toolkit/library/moz.build'
s=io.open(p,encoding='utf-8').read()
for name in ['        # Phase 1 hardware video decoding (OH_AVCodec)\n        "native_media_codecbase",\n        "native_media_core",\n        "native_media_vdec",\n']:
    s=s.replace(name,'')
io.open(p,'w',encoding='utf-8').write(s)
print('codec OS_LIBS removed')
