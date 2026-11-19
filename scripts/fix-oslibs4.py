import io,re
p='/home/dev/ff/gecko/toolkit/library/moz.build'
s=io.open(p,encoding='utf-8').read()
if 'native_media_vdec' not in s:
    a='        "ohinput",\n    ]'
    assert s.count(a)==1
    s=s.replace(a,'        "ohinput",\n        # Phase 1 hardware video decoding (OH_AVCodec)\n        "native_media_codecbase",\n        "native_media_core",\n        "native_media_vdec",\n    ]')
io.open(p,'w',encoding='utf-8').write(s)
# clean ohos/moz.build OS_LIBS/LDFLAGS
p2='/home/dev/ff/gecko/dom/media/platforms/ohos/moz.build'
s2=io.open(p2,encoding='utf-8').read()
s2=re.sub(r'\nLDFLAGS \+= \[[^\]]*\]\n','',s2)
s2=re.sub(r'\nOS_LIBS \+= \[[^\]]*\]\n','',s2)
io.open(p2,'w',encoding='utf-8').write(s2)
print('libs moved to toolkit/library')
