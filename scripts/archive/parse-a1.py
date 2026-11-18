import json
for f in ['a1']:
    d=json.load(open(f'/mnt/d/ff-ohos/logs/{f}.json',encoding='utf-8'))
    def walk(n):
        if not isinstance(n,dict): return
        a=n.get('attributes') or {}
        t=a.get('text') or ''
        if t in ('更多','刷新页面','后退','前进','复制页面地址','复制页面标题'):
            print(t, a.get('bounds'))
        for c in n.get('children') or []: walk(c)
    walk(d)
