#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

data = json.load(open('/mnt/d/ff-ohos/logs/layout2.json', encoding='utf-8'))

found = []
def walk(node):
    if not isinstance(node, dict):
        return
    a = node.get('attributes') or {}
    if a.get('clickable') == 'true' and a.get('bounds'):
        try:
            p = a['bounds'].replace('][', ',').strip('[]').split(',')
            x1, y1, x2, y2 = [int(v) for v in p]
        except Exception:
            x1 = y1 = x2 = y2 = -1
        w, h = x2 - x1, y2 - y1
        if 180 <= y1 <= 480 and x1 < 1200:
            found.append((y1, x1, x2, y2, w, h, a.get('text', ''), a.get('type')))
    for c in node.get('children') or []:
        walk(c)

walk(data)
for y1, x1, x2, y2, w, h, t, ty in sorted(found):
    print(f'y={y1}..{y2} x={x1}..{x2} ({w}x{h}) text={t!r} type={ty}')
