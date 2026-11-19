import io,re
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
s=re.sub(r"const BENCH_PAGE_HTML[^\n]*=.*?(?=\nexport default class)","",s,flags=re.S)
s=re.sub(r"      const benchPath = this\.context\.filesDir \+ '/bench\.html';\n(?:.|\n)*?      \}, 12000\);","      GeckoViewBoot.init('https://example.com/', dir);",s)
s=s.replace("import { GeckoEngine } from 'gecko';\n","")
assert 'BENCH' not in s and 'benchPath' not in s
io.open(p,'w',encoding='utf-8').write(s)
print('reverted')
