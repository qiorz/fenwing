import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
if 'codecProbe' not in s:
    a="          GeckoViewBoot.setBoolPref('ohos.menu.autotest', AppStorage.get<boolean>('menuAuto') === true);"
    assert s.count(a)==1
    s=s.replace(a, a+"""
          try {
            const codecs: string = GeckoEngine.codecProbe();
            hilog.info(DOMAIN, 'GeckoBoot', 'video decoders: %{public}s', codecs.substring(0, 1500));
          } catch (probeError) {
            hilog.warn(DOMAIN, 'GeckoBoot', 'codec probe failed');
          }""")
    io.open(p,'w',encoding='utf-8').write(s)
print('probe log wired')
