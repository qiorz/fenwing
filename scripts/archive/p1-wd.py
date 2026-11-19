import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
a="""    this.currentUrl = this.geckoUrl;
    const activeTabId: string = this.viewModel.getActiveTabId();"""
assert s.count(a)==1
s=s.replace(a,"""    this.currentUrl = this.geckoUrl;
    this.stopLoadWatchdog();
    const activeTabId: string = this.viewModel.getActiveTabId();""")
b="""    this.currentTitle = event.title;"""
assert s.count(b)==1
s=s.replace(b,"""    this.currentTitle = event.title;
    this.stopLoadWatchdog();""")
io.open(p,'w',encoding='utf-8').write(s)
print('watchdog cleared on url/title')
