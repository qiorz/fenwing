import io,json
# AppScope app_name
p='/mnt/d/ff-ohos/work/firefoxport/AppScope/resources/base/element/string.json'
d=json.load(io.open(p,encoding='utf-8'))
for s in d['string']:
    if s['name']=='app_name': s['value']='Fenwing'
io.open(p,'w',encoding='utf-8',newline='\n').write(json.dumps(d,ensure_ascii=False,indent=2))
# entry label/desc
p2='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/resources/base/element/string.json'
d2=json.load(io.open(p2,encoding='utf-8'))
for s in d2['string']:
    if s['name']=='EntryAbility_label': s['value']='Fenwing'
    if s['name']=='EntryAbility_desc': s['value']='Gecko 内核驱动浏览器'
io.open(p2,'w',encoding='utf-8',newline='\n').write(json.dumps(d2,ensure_ascii=False,indent=2))
print('renamed to Fenwing')
