import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
a="    await this.refreshPanels();\n    this.syncTabs();"
assert s.count(a)==1
s=s.replace(a,"""    await this.refreshPanels();
    this.syncTabs();
    if (this.geckoMenuSeq > 0) {
      this.onMenuEvent();
    }""")
io.open(p,'w',encoding='utf-8').write(s)
print('menu bootstrap trigger added')
