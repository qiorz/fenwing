#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys

path = '/mnt/d/ff-ohos/logs/layout2.json'
data = json.load(open(path, encoding='utf-8'))

def walk(node, depth=0):
    if not isinstance(node, dict):
        return
    attrs = node.get('attributes') or {}
    clickable = attrs.get('clickable') == 'true'
    bounds = attrs.get('bounds', '')
    text = attrs.get('text', '') or ''
    if clickable and bounds:
        try:
            parts = bounds.replace('][', ',').strip('[]').split(',')
            x1, y1, x2, y2 = [int(p) for p in parts]
        except Exception:
            return
        w, h = x2 - x1, y2 - y1
        if (1560 <= y1 <= 1720) or (230 <= y1 <= 340):
            print(f'clickable x={x1}..{x2} y={y1}..{y2} ({w}x{h}) text={text!r} type={attrs.get("type")}')
    for child in node.get('children') or []:
        walk(child, depth + 1)

walk(data)
