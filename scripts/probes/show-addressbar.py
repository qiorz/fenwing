import io
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()
i = s.find('AddressBar({')
print(s[i:i + 800])
print('--- states ---')
for line in s.splitlines():
    if 'canGoBack' in line or 'canGoForward' in line:
        print(line.strip())
