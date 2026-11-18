import json
d=json.load(open('/mnt/d/ff-ohos/logs/a2.json',encoding='utf-8'))
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t in ('更多','复制页面地址','复制页面标题'):
        print(t, a.get('bounds'))
    for c in n.get('children') or []: walk(c)
walk(d)
