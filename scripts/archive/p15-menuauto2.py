import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="    AppStorage.setOrCreate('debugCtxMenu', this.paramIsOne(want, 'ctxmenu'));"
assert s.count(a)==1
s=s.replace(a, a+"\n    AppStorage.setOrCreate('menuAuto', this.paramIsOne(want, 'menuauto'));")
s=s.replace("GeckoViewBoot.setBoolPref('ohos.menu.autotest', this.paramIsOne(want, 'menuauto'));",
            "GeckoViewBoot.setBoolPref('ohos.menu.autotest', AppStorage.get<boolean>('menuAuto') === true);")
io.open(p,'w',encoding='utf-8').write(s)
print('menuauto param fixed')
