import io
# geckoview.js: auto-open popup when pref ohos.menu.autotest=true
p='/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s=io.open(p,encoding='utf-8').read()
if 'ohos.menu.autotest' not in s:
    a="""  setTimeout(ohosNotifyActiveTitle, 1200);
  setTimeout(ohosNotifyActiveTitle, 3000);"""
    assert s.count(a)==1
    s=s.replace(a, a+"""
  setTimeout(function () {
    try {
      if (Services.prefs.getBoolPref("ohos.menu.autotest", false)) {
        const b = TabManager.getBrowserBySessionId(TabManager._selectedSessionId);
        if (b) {
          ohosOpenContextMenu(b, 420, 300);
          dump("[OHOS_CTX] autotest popup opened\\n");
        }
      }
    } catch (e) {
      dump(`[OHOS_CTX] autotest failed: ${e}\\n`);
    }
  }, 6000);""")
    io.open(p,'w',encoding='utf-8').write(s)
print('autotest hook added')

# EntryAbility: set autotest pref too
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="          GeckoViewBoot.setBoolPref('ohos.menu.native_overlay', true);"
assert s.count(a)==1
if 'ohos.menu.autotest' not in s:
    s=s.replace(a, a+"\n          GeckoViewBoot.setBoolPref('ohos.menu.autotest', this.paramIsOne(want, 'menuauto'));")
    io.open(p,'w',encoding='utf-8').write(s)
print('autotest pref wired')
