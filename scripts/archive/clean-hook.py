import io,re
R='/mnt/d/ff-ohos/work/firefoxport'
p=R+'/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
# remove diag hook + GeckoEngine import
s=re.sub(r"\n      setTimeout\(\(\) => \{\n        const tail = GeckoEngine[^\n]*\n(?:.|\n)*?\n      \}, 12000\);","",s)
s=s.replace("import { GeckoEngine } from 'gecko';\n","")
assert 'readLogTail' not in s
io.open(p,'w',encoding='utf-8').write(s)
print('clean:', 'BENCH' not in s)
