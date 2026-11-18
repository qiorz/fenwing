import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
i=s.find('private retryLoad')
print(s[i:i+500])
print('--- watchdog methods ---')
j=s.find('private startLoadWatchdog')
print(s[j:j+700])
