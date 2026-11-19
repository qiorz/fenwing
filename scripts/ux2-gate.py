import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
old="if (title.length > 0 || session === '__opentab__') {"
assert s.count(old)==1
s=s.replace(old,"if (title.length > 0 || session === '__opentab__' || session === '__scroll__') {")
io.open(p,'w',encoding='utf-8').write(s)
print('scroll gate ok')
