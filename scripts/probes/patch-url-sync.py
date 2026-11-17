import io
# 1) TabViewModel: quiet URL setter
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/viewmodel/TabViewModel.ets'
s=io.open(p,encoding='utf-8').read()
if 'setUrl(' not in s:
    a="""  markLoaded(tabId: string, title: string): void {"""
    assert s.count(a)==1
    s=s.replace(a, """  /** Updates the tab URL without touching the loading state (engine URL sync). */
  setUrl(tabId: string, url: string): void {
    const tab = this.findById(tabId);
    if (tab === undefined) {
      return;
    }
    if (tab.url === url) {
      return;
    }
    tab.url = url;
    this.notify();
  }

""" + a)
    io.open(p,'w',encoding='utf-8').write(s)
print('TabViewModel setUrl ok')

# 2) BrowserPage: engine URL writes model + address bar stays engine-driven
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
if 'setUrl(activeTabId' not in s:
    a="""    this.currentUrl = this.geckoUrl;
    const activeTabId: string = this.viewModel.getActiveTabId();
    if (activeTabId.length > 0) {
      this.engineUrlByTab.set(activeTabId, this.geckoUrl);
    }"""
    assert s.count(a)==1
    s=s.replace(a, """    this.currentUrl = this.geckoUrl;
    const activeTabId: string = this.viewModel.getActiveTabId();
    if (activeTabId.length > 0) {
      this.engineUrlByTab.set(activeTabId, this.geckoUrl);
      this.viewModel.setUrl(activeTabId, this.geckoUrl);
    }""")
    io.open(p,'w',encoding='utf-8').write(s)
print('BrowserPage url sync ok')
