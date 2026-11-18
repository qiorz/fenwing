import io
R='/mnt/d/ff-ohos/work/firefoxport'
# EntryAbility: ctxmenu param
p=R+'/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="    AppStorage.setOrCreate('skipResume', this.paramIsOne(want, 'noresume'));"
assert s.count(a)==1
if 'debugCtxMenu' not in s:
    s=s.replace(a, a+"\n    AppStorage.setOrCreate('debugCtxMenu', this.paramIsOne(want, 'ctxmenu'));")
    io.open(p,'w',encoding='utf-8').write(s)

# BrowserPage: field + trigger
p=R+'/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
if 'debugCtxMenu' not in s:
    a="  @StorageProp('skipResume') skipResume: boolean = false;"
    assert s.count(a)==1
    s=s.replace(a, a+"\n  @StorageProp('debugCtxMenu') debugCtxMenu: boolean = false;")
    a="""    if (this.engineRenderReady) {
      this.startLoadWatchdog();
    }
    await this.refreshPanels();"""
    assert s.count(a)==1
    s=s.replace(a, """    if (this.engineRenderReady) {
      this.startLoadWatchdog();
    }
    if (this.debugCtxMenu) {
      setTimeout(() => {
        const size = GeckoViewBoot.surfaceSize();
        const cx: number = Math.round(size.width / 2);
        const cy: number = Math.round(size.height / 2);
        hilog.info(DOMAIN, TAG, 'ctxmenu probe at %{public}d,%{public}d', cx, cy);
        GeckoViewBoot.mouseDown(cx, cy, 2);
        setTimeout(() => {
          GeckoViewBoot.mouseUp(cx, cy, 2);
        }, 80);
      }, 4000);
    }
    await this.refreshPanels();""")
    io.open(p,'w',encoding='utf-8').write(s)
print('ctxmenu probe wired')
