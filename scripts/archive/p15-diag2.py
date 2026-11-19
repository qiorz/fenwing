import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="    AppStorage.setOrCreate('menuAuto', this.paramIsOne(want, 'menuauto'));"
assert s.count(a)==1
s=s.replace(a, a+"\n    AppStorage.setOrCreate('diagMode', this.paramIsOne(want, 'diag'));")
s=s.replace("if (this.paramIsOne(want, 'diag')) {","if (AppStorage.get<boolean>('diagMode') === true) {",1)
io.open(p,'w',encoding='utf-8').write(s)
print('diag param fixed')
