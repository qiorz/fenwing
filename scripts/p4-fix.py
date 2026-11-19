import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/Index.ets'
b=open(p,'rb').read()
if b.startswith(b'\xef\xbb\xbf'): b=b[3:]
s=b.decode('utf-8',errors='replace')
s=s.replace('\r\n','\n').replace('Firefox 鍩虹嚎','Gecko 内核基线')
s=s.replace('Firefox 基线','Gecko 内核基线')
open(p,'w',encoding='utf-8',newline='\n').write(s)
print('index fixed', s.count('Gecko 内核基线'))
p2='/mnt/d/ff-ohos/work/firefoxport/AppScope/resources/base/element/string.json'
b=open(p2,'rb').read()
if b.startswith(b'\xef\xbb\xbf'): b=b[3:]
open(p2,'wb').write(b)
print('string.json bom stripped')
