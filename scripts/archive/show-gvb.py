import io
p = '/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s = io.open(p, encoding='utf-8').read()
i = s.find('onIme')
print('onIme at', i)
print(repr(s[i-300:i+300]))
