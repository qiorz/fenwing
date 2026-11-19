import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
if 'softDecode' not in s:
    s=s.replace("AppStorage.setOrCreate('diagMode', this.paramIsOne(want, 'diag'));",
                "AppStorage.setOrCreate('diagMode', this.paramIsOne(want, 'diag'));\n    AppStorage.setOrCreate('softDecode', this.paramIsOne(want, 'swdecode'));")
    s=s.replace("GeckoViewBoot.setBoolPref('ohos.menu.native_overlay', true);",
                "GeckoViewBoot.setBoolPref('ohos.menu.native_overlay', true);\n    GeckoViewBoot.setBoolPref('media.ohos.hw_decode', !(AppStorage.get<boolean>('softDecode') === true));")
io.open(p,'w',encoding='utf-8').write(s)
print('EntryAbility softDecode wired:', 'softDecode' in s)
