import io
p = '/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s = io.open(p, encoding='utf-8').read()
idx = s.find('handlers.onIme')
print('first handlers.onIme at', idx)
print(repr(s[idx-260:idx+320]))
print('onTitle present:', 'onTitle' in s)
