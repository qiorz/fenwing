import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="    this.bootGecko(perf, nojit, this.stringParam(want, 'url'), this.paramIsOne(want, 'demo'));"
assert s.count(a)==1
s=s.replace(a,"    this.bootGecko(perf, nojit, this.stringParam(want, 'url'), this.paramIsOne(want, 'demo'), this.paramIsOne(want, 'menutest'));")
s=s.replace("  private bootGecko(perf: boolean, nojit: boolean, overrideUrl: string, demo: boolean): void {",
            "  private bootGecko(perf: boolean, nojit: boolean, overrideUrl: string, demo: boolean, menuTest: boolean): void {",1)
s=s.replace("      if (this.paramIsOne(want, 'menutest')) {","      if (menuTest) {")
io.open(p,'w',encoding='utf-8').write(s)
print('menutest param fixed')
