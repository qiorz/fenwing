import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old='this.engineRenderReady = version.availability === EngineAvailability.READY;'
new='this.engineRenderReady = bridgeReady || version.availability === EngineAvailability.READY;'
assert s.count(old)==1, s.count(old)
io.open(p,'w',encoding='utf-8').write(s.replace(old,new))
print('engineRenderReady patched')
