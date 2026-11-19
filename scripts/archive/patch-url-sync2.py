import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
a="""    this.currentUrl = this.geckoUrl;
    hilog.info(DOMAIN, TAG, 'engine url -> %{public}s (session=%{public}s)', this.geckoUrl, this.geckoSession);"""
assert s.count(a)==1, s.count(a)
s=s.replace(a, """    this.currentUrl = this.geckoUrl;
    const activeTabId: string = this.viewModel.getActiveTabId();
    if (activeTabId.length > 0) {
      this.viewModel.setUrl(activeTabId, this.geckoUrl);
    }
    hilog.info(DOMAIN, TAG, 'engine url -> %{public}s (session=%{public}s)', this.geckoUrl, this.geckoSession);""")
io.open(p,'w',encoding='utf-8').write(s)
print('url->model sync ok')
