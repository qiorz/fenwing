import io
# EntryAbility
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
if "geckoTitle" not in s:
    a="""        onIme: (state: string) => {
          AppStorage.setOrCreate('geckoImeState', state);
        }"""
    assert s.count(a)==1
    s=s.replace(a, a+""",
        onTitle: (title: string, url: string, session: string) => {
          if (title.length > 0) {
            AppStorage.setOrCreate('geckoTitle', title);
          }
        }""")
    io.open(p,'w',encoding='utf-8').write(s)
print('EntryAbility ok')

# BrowserPage
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
if '<title>新标签页</title>' not in s:
    old="const START_PAGE_HTML: string = 'data:text/html,' + encodeURIComponent(\n  '<html><body style="
    assert s.count(old)==1
    s=s.replace(old, "const START_PAGE_HTML: string = 'data:text/html,' + encodeURIComponent(\n  '<html><head><title>新标签页</title></head><body style=")
io.open(p,'w',encoding='utf-8').write(s)
print('BrowserPage ok')
