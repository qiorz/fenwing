import io,re
R='/mnt/d/ff-ohos/work/firefoxport'
# restore JIT flag
p=R+'/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace("      commandlineArgs: '--airweb-force-no-jit',","      commandlineArgs: '',")
io.open(p,'w',encoding='utf-8').write(s)
# restore normal entry page
p=R+'/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
s=re.sub(r"const BENCH_PAGE_HTML[^\n]*=.*?(?=\nexport default class)","",s,flags=re.S)
s=re.sub(r"      const bp = this\.context\.filesDir \+ '/bench\.html';\n(?:.|\n)*?      GeckoViewBoot\.init\('file://' \+ bp, dir\);","      GeckoViewBoot.init('https://example.com/', dir);",s)
assert 'BENCH' not in s and 'file://' not in s
io.open(p,'w',encoding='utf-8').write(s)
print('restored')
