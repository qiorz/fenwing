import io
p='/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
a="      commandlineArgs: '',"
assert s.count(a)==1
io.open(p,'w',encoding='utf-8').write(s.replace(a,"      commandlineArgs: '--airweb-force-no-jit',"))
print('interp flag set')
