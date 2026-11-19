import io, base64
svg = b'''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><rect width="240" height="240" fill="#4C6FFF"/><circle cx="120" cy="120" r="60" fill="#FFD166"/><text x="120" y="130" font-size="28" text-anchor="middle" fill="#12121A">IMG</text></svg>'''
b64 = base64.b64encode(svg).decode()
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
import re
start=s.find('<img id="img" src="data:image/png;base64,')
assert start>0
end=s.find('" width="240" height="240">', start)+len('" width="240" height="240">')
new='<img id="img" src="data:image/svg+xml;base64,' + b64 + '" width="240" height="240">'
s=s[:start]+new+s[end:]
io.open(p,'w',encoding='utf-8').write(s)
print('svg image embedded')
