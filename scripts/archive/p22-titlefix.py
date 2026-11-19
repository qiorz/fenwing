import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
old="""        onTitle: (title: string, url: string, session: string) => {
          if (title.length > 0) {"""
assert s.count(old)==1
s=s.replace(old,"""        onTitle: (title: string, url: string, session: string) => {
          if (title.length > 0 || session === '__opentab__') {""")
io.open(p,'w',encoding='utf-8').write(s)
print('title gate fixed')
