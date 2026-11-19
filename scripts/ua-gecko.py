import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace("ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';",
            "ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0';")
s=s.replace("ua = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36';",
            "ua = 'Mozilla/5.0 (Android 13; Mobile; rv:142.0) Gecko/142.0 Firefox/142.0';")
s=s.replace("ua = 'Mozilla/5.0 (Linux; HarmonyOS 5.0; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';",
            "ua = 'Mozilla/5.0 (HarmonyOS 5.0; Mobile; rv:142.0) Gecko/142.0 Firefox/142.0';")
io.open(p,'w',encoding='utf-8').write(s)
print('UA switched to Gecko/Firefox style')
