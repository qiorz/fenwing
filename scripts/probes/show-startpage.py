import io
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()
i = s.find('START_PAGE_HTML')
print(repr(s[i-60:i+240]))
print('onGeckoTitleChanged present:', 'onGeckoTitleChanged' in s)
print('geckoTitle present:', 'geckoTitle' in s)
