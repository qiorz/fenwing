import io
p='/home/dev/ff/gecko/mozconfig'
s=io.open(p,encoding='utf-8').read()
s=s.replace('ac_add_options --disable-webcodecs\n','').replace('ac_add_options --disable-webgpu\n','')
io.open(p,'w',encoding='utf-8').write(s)
print('removed webcodecs/webgpu flags')
