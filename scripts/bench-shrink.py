import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
repl=[('i<20000000','i<3000000'),('i<2000000','i<300000'),('i<200000;','i<20000;'),('i<100000;','i<20000;'),('i<300000;','i<30000;')]
for a,b in repl:
    assert a in s, a
    s=s.replace(a,b)
io.open(p,'w',encoding='utf-8').write(s)
print('bench sizes reduced')
