import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="import { GeckoViewBoot, GeckoViewHandlers } from 'gecko';"
if 'readLogTail' not in s:
    s=s.replace(a,a+"\nimport { GeckoEngine } from 'gecko';")
    old="      GeckoViewBoot.init('https://example.com/', dir);"
    assert s.count(old)==1
    s=s.replace(old, old+"""
      setTimeout(() => {
        const tail = GeckoEngine.readLogTail(`${this.context.filesDir}/gecko_xre_diag.txt`, 30000);
        for (let i = 0; i < tail.length; i += 1000) {
          hilog.info(DOMAIN, 'Diag', '%{public}s', tail.substring(i, i + 1000));
        }
      }, 12000);""")
    io.open(p,'w',encoding='utf-8').write(s)
print('diag hook added')
