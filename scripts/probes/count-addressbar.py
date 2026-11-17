import io
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()
print('AddressBar( occurrences:', s.count('AddressBar({'))
idx = 0
while True:
    i = s.find('AddressBar({', idx)
    if i < 0:
        break
    print('---- at', i, '----')
    print(s[i:i + 260])
    idx = i + 1
