import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
i=s.find('onGeckoPageLoadChanged(): void')
print(s[i-200:i+500])
