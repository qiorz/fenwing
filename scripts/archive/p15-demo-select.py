import io,re
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
old="'<p><input type=\"file\" id=\"f\" style=\"font-size:26px;width:620px\"></p>'"
assert s.count(old)==1, s.count(old)
new="'<p><input type=\"file\" id=\"f\" style=\"font-size:26px;width:620px\"></p>'\n        '<p><select id=\"s\" style=\"font-size:26px;padding:10px\"><option>AAA</option><option>BBB</option><option>CCC</option></select></p>'"
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('select added to demo page')
