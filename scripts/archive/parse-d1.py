import json
d=json.load(open('/mnt/d/ff-ohos/logs/d1.json',encoding='utf-8'))
want=['下载','书签','历史','设置']
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t in want:
        print(t, a.get('bounds'), a.get('clickable'))
    for c in n.get('children') or []: walk(c)
walk(d)
