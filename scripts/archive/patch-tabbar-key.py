import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/components/TabBar.ets'
s=io.open(p,encoding='utf-8').read()
old="""        }, (chip: TabChip) => chip.id)"""
assert s.count(old)==1, s.count(old)
new="""        }, (chip: TabChip) => `${chip.id}|${chip.title}|${chip.id === this.activeTabId}`)"""
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('TabBar key patched')
