import io
src='/mnt/d/ff-ohos/refs/firefoxport/entry/src/main/ets/pages/Index.ets'
dst='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/Index.ets'
s=io.open(src,encoding='utf-8').read()
s=s.replace('Firefox 基线','Gecko 内核基线')
io.open(dst,'w',encoding='utf-8',newline='\n').write(s)
print('restored Index.ets, len', len(s))
