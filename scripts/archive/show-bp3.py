import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
i=s.find('const bridgeReady')
print(s[i:i+1400])
print('==== build head ====')
j=s.find('  build() {')
print(s[j:j+900])
