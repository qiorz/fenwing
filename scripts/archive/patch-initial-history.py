import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
a="    this.bindEngineSession(firstTab.id, 0);"
assert s.count(a)==1
s=s.replace(a, a+"\n    this.pushHistory(firstTab.id, 'https://example.com/');")
b="""          this.bindEngineSession(created.id, engineIndex);
          const engineUrl: string = modelUrl === 'about:newtab' ? 'https://example.org/' : modelUrl;
          GeckoViewBoot.createSession(engineIndex, engineUrl);"""
assert s.count(b)==1, s.count(b)
s=s.replace(b, """          this.bindEngineSession(created.id, engineIndex);
          const engineUrl: string = modelUrl === 'about:newtab' ? 'https://example.org/' : modelUrl;
          this.pushHistory(created.id, engineUrl);
          GeckoViewBoot.createSession(engineIndex, engineUrl);""")
io.open(p,'w',encoding='utf-8').write(s)
print('initial history entries added')
