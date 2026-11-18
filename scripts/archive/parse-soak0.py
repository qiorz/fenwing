import json
d=json.load(open('/mnt/d/ff-ohos/logs/soak0.json',encoding='utf-8'))
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t in ('+','☰','例','Example Domain') or (t and 'Domain' in t):
        print(repr(t), a.get('bounds'), a.get('clickable'))
    for c in n.get('children') or []: walk(c)
walk(d)
