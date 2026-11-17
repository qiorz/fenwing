import io
p='/mnt/d/ff-ohos/scripts/p0-browserpage.py'
s=io.open(p,encoding='utf-8').read()
old='''rep("""  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
  }""",
    """  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
    if (this.loading) {
      this.loadError = '';
      this.startLoadWatchdog();
    } else {
      this.stopLoadWatchdog();
    }
  }""")'''
new='''rep("""  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
    if (this.geckoPageLoad === 'stop') {
      this.refreshHistoryState();
    }
  }""",
    """  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
    if (this.loading) {
      this.loadError = '';
      this.startLoadWatchdog();
    } else {
      this.stopLoadWatchdog();
      this.refreshHistoryState();
    }
  }""")'''
assert s.count(old)==1
io.open(p,'w',encoding='utf-8').write(s.replace(old,new))
print('script anchor fixed')
