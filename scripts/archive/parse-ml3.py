import json
d=json.load(open('/mnt/d/ff-ohos/logs/ml3.json',encoding='utf-8'))
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t in ('刷新页面','后退','前进','复制页面地址','菜单'): 
        print(repr(t), a.get('bounds'))
    for c in n.get('children') or []: walk(c)
walk(d)
