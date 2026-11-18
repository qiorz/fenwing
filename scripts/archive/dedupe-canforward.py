import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
line='  @State private canGoForward: boolean = false;\n'
n=s.count(line)
print('count', n)
if n>1:
    # remove the second occurrence
    first=s.find(line)
    second=s.find(line, first+len(line))
    s=s[:second]+s[second+len(line):]
    io.open(p,'w',encoding='utf-8').write(s)
    print('deduped')
