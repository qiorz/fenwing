import io
p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s = io.open(p, encoding='utf-8').read()
i = s.find('createBrowserForSession')
print('occurrences:', s.count('createBrowserForSession'))
j = s.find('return browser;', i)
print(repr(s[j-200:j+120]))
