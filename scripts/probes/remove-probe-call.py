import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/service/GeckoService.ets'
s=io.open(p,encoding='utf-8').read()
i=s.find("      try {\n        hilog.info(DOMAIN, TAG, 'JIT probe:")
if i>=0:
    j=s.find("      }\n", s.find("'JIT probe failed');", i))+len("      }\n")
    s=s[:i]+s[j:]
    io.open(p,'w',encoding='utf-8').write(s)
print('probe call removed')
