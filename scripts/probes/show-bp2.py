import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
i=s.find('aboutToAppear')
print('aboutToAppear at', i)
print(s[i:i+1400])
print('==== syncTabs ====')
j=s.find('private syncTabs')
print(s[j:j+1000])
