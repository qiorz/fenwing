import io
p='/home/dev/ff/gecko/mozconfig'
s=io.open(p,encoding='utf-8').read()
if '--disable-webrtc' not in s:
    s=s.rstrip()+'\nac_add_options --disable-webrtc\n'
    io.open(p,'w',encoding='utf-8').write(s)
print('webrtc disabled in mozconfig')
