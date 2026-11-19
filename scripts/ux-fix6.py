import io,re
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
bad=s[s.find('statusMessage = `'):s.find('`;',s.find('statusMessage = `'))+2]
print('BAD:',bad[:80])
s=s.replace(bad,'statusMessage = `设置读取失败：${JSON.stringify(error)}`;')
s=s.replace('    this.applyUserAgent();\n    if (this.debugCtxMenu) {','    setTimeout(() => {\n      this.applyUserAgent();\n    }, 2000);\n    if (this.debugCtxMenu) {')
s=s.replace("      GeckoViewBoot.setCharPref('general.useragent.override', ua);","      GeckoViewBoot.setCharPref('general.useragent.override', ua);\n      hilog.info(DOMAIN, TAG, 'ua applied mode=%{public}s', this.uaMode);")
io.open(p,'w',encoding='utf-8').write(s)
print('fixed')
