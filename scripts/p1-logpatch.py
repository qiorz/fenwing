import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace("timestamp,widget:5,Compositor:5,WebRender:5,gl:5,gfx:5,DomRef:5,nsHttp:5,nsSocketTransport:5,nsHostResolver:5,pipnss:5",
            "timestamp,widget:5,Compositor:5,WebRender:5,gl:5,gfx:5,DomRef:5,nsHttp:5,nsSocketTransport:5,nsHostResolver:5,pipnss:5,OHOSDecoder:5,PlatformDecoderModule:5")
s=s.replace("const files: string[] = ['gecko_xre_diag.txt', 'gecko_debug.txt'];",
            "const files: string[] = ['gecko_xre_diag.txt', 'gecko_debug.txt', 'gecko_nspr.txt'];")
io.open(p,'w',encoding='utf-8').write(s)
print('mozlog+diag patched')
