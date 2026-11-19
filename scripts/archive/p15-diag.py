import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
if 'readLogTail' not in s:
    a="import { GeckoViewBoot, GeckoViewHandlers } from 'gecko';"
    assert s.count(a)==1
    s=s.replace(a, a+"\nimport { GeckoEngine } from 'gecko';")
    a="      const engineArgs: string = nojit ? '--airweb-force-no-jit' : '';"
    assert s.count(a)==1
    s=s.replace(a, a+"""
      if (this.paramIsOne(want, 'diag')) {
        setTimeout(() => {
          const files: string[] = ['gecko_xre_diag.txt', 'gecko_debug.txt'];
          for (let fi = 0; fi < files.length; fi++) {
            const tail: string = GeckoEngine.readLogTail(`${this.context.filesDir}/${files[fi]}`, 20000);
            for (let i = 0; i < tail.length; i += 1000) {
              hilog.info(DOMAIN, 'Diag', '%{public}s', tail.substring(i, i + 1000));
            }
          }
        }, 9000);
      }""")
    io.open(p,'w',encoding='utf-8').write(s)
print('diag dump wired')
