import io
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()
i = s.find('private onGeckoUrlChanged')
print(s[i - 120:i + 700])
