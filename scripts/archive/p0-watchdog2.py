import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()

# field
a="  private loadWatchdog: number = -1;"
assert s.count(a)==1
if 'loadSettled' not in s:
    s=s.replace(a,a+"\n  private loadSettled: boolean = true;")

# watchdog methods
old="""  private startLoadWatchdog(): void {
    this.stopLoadWatchdog();
    this.loadWatchdog = setTimeout(() => {
      if (this.loading) {
        this.loadError = '页面加载超时：请检查网络连接，或重试。';
        hilog.warn(DOMAIN, TAG, 'load watchdog fired');
      }
    }, 20000);
  }

  private stopLoadWatchdog(): void {
    if (this.loadWatchdog >= 0) {
      clearTimeout(this.loadWatchdog);
      this.loadWatchdog = -1;
    }
  }"""
assert s.count(old)==1
new="""  private startLoadWatchdog(): void {
    this.stopLoadWatchdog();
    this.loadSettled = false;
    this.loading = true;
    this.loadWatchdog = setTimeout(() => {
      if (!this.loadSettled) {
        this.loadError = '页面加载超时：请检查网络连接，或重试。';
        this.loading = false;
        hilog.warn(DOMAIN, TAG, 'load watchdog fired');
      }
    }, 20000);
  }

  private stopLoadWatchdog(): void {
    this.loadSettled = true;
    if (this.loadWatchdog >= 0) {
      clearTimeout(this.loadWatchdog);
      this.loadWatchdog = -1;
    }
  }"""
s=s.replace(old,new)

# arm after bootstrap engine ready
a="    } else {\n      const firstTab = this.viewModel.createTab(TabViewModel.homeUrl());"
assert s.count(a)==1
s=s.replace(a,"""    } else {
      const firstTab = this.viewModel.createTab(TabViewModel.homeUrl());""")
a2="      this.viewModel.markLoaded(firstTab.id, 'Example Domain');\n    }"
assert s.count(a2)==1
s=s.replace(a2,"""      this.viewModel.markLoaded(firstTab.id, 'Example Domain');
    }
    if (this.engineRenderReady) {
      this.startLoadWatchdog();
    }""")

# arm on navigate
a3="        this.pushHistory(tabId, resolved);"
assert s.count(a3)==1
s=s.replace(a3,"        this.pushHistory(tabId, resolved);\n        this.startLoadWatchdog();")

# retry arms too
old_retry="""  private retryLoad(): void {
    this.loadError = '';
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex !== undefined) {
      GeckoViewBoot.reloadForSession(engineIndex);
      this.repaintSoon();
    }
  }"""
assert s.count(old_retry)==1
s=s.replace(old_retry,"""  private retryLoad(): void {
    this.loadError = '';
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex !== undefined) {
      GeckoViewBoot.reloadForSession(engineIndex);
      this.repaintSoon();
      this.startLoadWatchdog();
    }
  }""")

io.open(p,'w',encoding='utf-8').write(s)
print('watchdog improved')
