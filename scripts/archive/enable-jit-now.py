import io
ROOT='/mnt/d/ff-ohos/work/firefoxport'
p=ROOT+'/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
a="      commandlineArgs: '--airweb-force-no-jit',"
assert s.count(a)==1
s=s.replace(a,"      // ACL granted: XPCOMInit RWX probe enables the full JIT backend.\n      commandlineArgs: '',")
io.open(p,'w',encoding='utf-8').write(s)
p=ROOT+'/entry/src/main/ets/service/GeckoService.ets'
s=io.open(p,encoding='utf-8').read()
if 'probeJit' not in s:
    a="      hilog.info(DOMAIN, TAG, 'Native bridge initialized');"
    assert s.count(a)==1
    s=s.replace(a,a+"\n      try {\n        hilog.info(DOMAIN, TAG, 'JIT probe: %{public}s', GeckoEngine.probeJit());\n      } catch (probeError) {\n        hilog.warn(DOMAIN, TAG, 'JIT probe failed');\n      }")
    io.open(p,'w',encoding='utf-8').write(s)
print('JIT enabled + probe wired')
