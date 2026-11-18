import io
# wrapper: pass int32 (port expects 0/1)
p='/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
a="    geckoview.setBoolPref(name, value);"
assert s.count(a)==1
s=s.replace(a,"    geckoview.setBoolPref(name, value ? 1 : 0);")
io.open(p,'w',encoding='utf-8').write(s)
# d.ts: value is number
p='/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/cpp/types/libgeckoview/index.d.ts'
s=io.open(p,encoding='utf-8').read()
s=s.replace("export const setBoolPref: (name: string, value: boolean) => void;","export const setBoolPref: (name: string, value: number) => void;")
io.open(p,'w',encoding='utf-8').write(s)
print('setBoolPref int fixed')
