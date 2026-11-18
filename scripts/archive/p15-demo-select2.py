import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
old='<p><button onclick="dl()'
assert s.count(old)==1
new='<p><select id="s" style="font-size:26px;padding:10px"><option>AAA</option><option>BBB</option><option>CCC</option></select></p><p><button onclick="dl()'
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('select inserted')
