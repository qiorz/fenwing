import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
if 'onGeckoTitleChanged' not in s:
    a="  @StorageProp('geckoPageLoad') @Watch('onGeckoPageLoadChanged') geckoPageLoad: string = '';"
    assert s.count(a)==1
    s=s.replace(a, a+"\n  @StorageProp('geckoTitle') @Watch('onGeckoTitleChanged') geckoTitle: string = '';")
    a="  private onGeckoPageLoadChanged(): void {"
    assert s.count(a)==1
    s=s.replace(a, """  /** Real page title from the engine keeps the tab chip and header in sync. */
  private onGeckoTitleChanged(): void {
    if (this.geckoTitle.length === 0) {
      return;
    }
    this.currentTitle = this.geckoTitle;
    const activeTabId: string = this.viewModel.getActiveTabId();
    if (activeTabId.length > 0) {
      this.viewModel.markLoaded(activeTabId, this.geckoTitle);
      this.syncTabs();
    }
  }

  private onGeckoPageLoadChanged(): void {""")
    io.open(p,'w',encoding='utf-8').write(s)
print('BrowserPage title watch ok:', 'onGeckoTitleChanged' in io.open(p,encoding='utf-8').read())
