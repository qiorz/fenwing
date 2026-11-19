import io
p='/home/dev/ff/gecko/toolkit/library/moz.build'
s=io.open(p,encoding='utf-8').read()
if 'aarch64-linux-ohos' not in s:
    s=s.rstrip()+'\n\nLDFLAGS += ["-L/opt/ohos-sdk/native/sysroot/usr/lib/aarch64-linux-ohos"]\n'
    io.open(p,'w',encoding='utf-8').write(s)
print('toolkit/library LDFLAGS added')
