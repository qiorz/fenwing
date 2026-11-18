import json
d=json.load(open('/mnt/d/ff-ohos/logs/layout6.json',encoding='utf-8'))
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t and ('Example' in t or '标签' in t):
        print('text=',repr(t),a.get('bounds'))
    for c in n.get('children') or []: walk(c)
walk(d)
