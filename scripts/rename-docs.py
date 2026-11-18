import io,glob,os
files=glob.glob('/mnt/d/dsh/homo移植/docs/*.md')+glob.glob('/mnt/d/ff-ohos/work/firefoxport/entry/src/main/resources/rawfile/legal/*.txt')
for p in files:
    try:
        s=io.open(p,encoding='utf-8').read()
    except Exception:
        continue
    if 'AirWeb' in s:
        io.open(p,'w',encoding='utf-8').write(s.replace('AirWeb','Fenwing'))
        print('updated',os.path.basename(p))
