import json
d=json.load(open('/mnt/d/ff-ohos/logs/ml.json',encoding='utf-8'))
want=['刷新页面','复制链接','显示工具栏','禁用项示例']
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t in want:
        print(repr(t), a.get('bounds'), a.get('clickable'))
    for c in n.get('children') or []: walk(c)
walk(d)
