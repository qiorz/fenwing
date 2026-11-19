import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/moz.build'
s=io.open(p,encoding='utf-8').read()
import re
s=re.sub(r'OS_LIBS \+= \[[^\]]*\]', '''OS_LIBS += [
    "/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos/libnative_media_codecbase.so",
    "/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos/libnative_media_core.so",
    "/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos/libnative_media_vdec.so",
]''', s, flags=re.S)
io.open(p,'w',encoding='utf-8').write(s)
print(s)
