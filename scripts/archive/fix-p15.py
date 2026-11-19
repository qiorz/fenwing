import io
p='/mnt/d/ff-ohos/scripts/p15-compact.py'
s=io.open(p,encoding='utf-8').read()
old='''    a = "      if (handlers.onDownload !== undefined) {"
    assert s.count(a) == 1
    s = s.replace(a, """      if (handlers.onMenu !== undefined) {'''
new='''    a = "\\n      if (handlers.onDownload !== undefined) {\\n        geckoview.registerDownloadCallback"
    assert s.count(a) == 1
    s = s.replace(a, """\\n      if (handlers.onMenu !== undefined) {
        geckoview.registerMenuCallback((json: string) => {
          if (handlers.onMenu !== undefined) {
            handlers.onMenu(json);
          }
        });
      }
      if (handlers.onDownload !== undefined) {\\n        geckoview.registerDownloadCallback'''
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('anchor fixed')
