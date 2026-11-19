import io,json
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/resources/base/element/string.json'
d=json.load(io.open(p,encoding='utf-8'))
for s in d['string']:
    if s['name']=='EntryAbility_label': s['value']='AirWeb'
    if s['name']=='EntryAbility_desc': s['value']='Gecko 内核驱动浏览器'
io.open(p,'w',encoding='utf-8',newline='\n').write(json.dumps(d,ensure_ascii=False,indent=2))
print('entry strings updated')
