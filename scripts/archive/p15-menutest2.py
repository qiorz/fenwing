import io,re
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
start=s.find('        const sample = JSON.stringify({')
end=s.find('        });\n        this.menuSeq += 1;', start)
assert start>0 and end>start, (start,end)
new = '''        const sample: string = '{"menuId":9001,"title":"","anchor":{"x":260,"y":180,"w":0,"h":0},"items":[' +
          '{"kind":"item","id":1,"label":"刷新页面","accel":"Ctrl+R","disabled":false,"checked":false,"hidden":false,"items":[]},' +
          '{"kind":"item","id":2,"label":"复制链接","accel":"Ctrl+C","disabled":false,"checked":false,"hidden":false,"items":[]},' +
          '{"kind":"separator","id":0,"label":"","accel":"","disabled":false,"checked":false,"hidden":false,"items":[]},' +
          '{"kind":"checkbox","id":3,"label":"显示工具栏","accel":"","disabled":false,"checked":true,"hidden":false,"items":[]},' +
          '{"kind":"item","id":4,"label":"禁用项示例","accel":"","disabled":true,"checked":false,"hidden":false,"items":[]}' +
          ']}';
'''
s = s[:start] + new + s[end+len('        });\n'):]
io.open(p,'w',encoding='utf-8').write(s)
print('sample stringified')
