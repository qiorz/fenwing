import json
d = json.load(open('/mnt/d/ff-ohos/logs/pl.json', encoding='utf-8'))
out = []
def walk(n):
    if not isinstance(n, dict):
        return
    a = n.get('attributes') or {}
    t = a.get('text') or ''
    if t in ('查找', '隐藏查找', '上一个', '下一个', '关闭') or '页内查找' in t:
        out.append((t, a.get('bounds'), a.get('clickable')))
    for c in n.get('children') or []:
        walk(c)
walk(d)
for row in out:
    print(row)
