import json
d=json.load(open('/mnt/d/ff-ohos/logs/p22m.json',encoding='utf-8'))
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    t=a.get('text') or ''
    if t in ('在新标签页打开链接','复制链接地址','保存图片','复制图片地址','刷新页面','更多'):
        print(repr(t), a.get('bounds'))
    for c in n.get('children') or []: walk(c)
walk(d)
