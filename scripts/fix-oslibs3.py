import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/moz.build'
s=io.open(p,encoding='utf-8').read()
s=s.replace('OS_LIBS += [\n    "/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos/libnative_media_codecbase.so",\n    "/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos/libnative_media_core.so",\n    "/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos/libnative_media_vdec.so",\n]',
'LDFLAGS += ["-L/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos"]\n\nOS_LIBS += [\n    "native_media_codecbase.so",\n    "native_media_core.so",\n    "native_media_vdec.so",\n]')
io.open(p,'w',encoding='utf-8').write(s)
print(s)
