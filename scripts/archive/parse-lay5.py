import json
d=json.load(open('/mnt/d/ff-ohos/logs/lay5.json',encoding='utf-8'))
want=['前往','−','+','☰','←','→','查找']
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t in want or (t and any(w in t for w in ['前往','查找'])):
        print(repr(t), a.get('bounds'), a.get('clickable'), a.get('visible'))
    for c in n.get('children') or []: walk(c)
walk(d)
