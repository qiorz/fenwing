import io
p='/mnt/d/ff-ohos/scripts/p0-watchdog2.py'
s=io.open(p,encoding='utf-8').read()
old='''a4="      GeckoViewBoot.reloadForSession(engineIndex);\\n      this.repaintSoon();"
assert s.count(a4)==1
s=s.replace(a4,"      GeckoViewBoot.reloadForSession(engineIndex);\\n      this.repaintSoon();\\n      this.startLoadWatchdog();")'''
new='''old_retry="""  private retryLoad(): void {
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
  }""")'''
assert s.count(old)==1
io.open(p,'w',encoding='utf-8').write(s.replace(old,new))
print('anchor fixed')
