import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/moz.build'
s=io.open(p,encoding='utf-8').read()
s=s.replace('"native_media_codecbase",','"native_media_codecbase.so",').replace('"native_media_core",','"native_media_core.so",').replace('"native_media_vdec",','"native_media_vdec.so",')
io.open(p,'w',encoding='utf-8').write(s)
print(s)
