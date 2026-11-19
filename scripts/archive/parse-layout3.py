import json
d=json.load(open('/mnt/d/ff-ohos/logs/layout3.json',encoding='utf-8'))
def walk(n):
    if not isinstance(n,dict): return
    a=n.get('attributes') or {}
    if a.get('bounds'):
        try:
            p=a['bounds'].replace('][',',').strip('[]').split(','); x1,y1,x2,y2=[int(v) for v in p]
        except: x1=y1=x2=y2=-1
        if 380<=y1<=500 and x1<1200:
            print(f"clickable={a.get('clickable')} enabled={a.get('enabled')} x={x1}..{x2} y={y1}..{y2} text={a.get('text')!r} type={a.get('type')}")
    for c in n.get('children') or []: walk(c)
walk(d)
