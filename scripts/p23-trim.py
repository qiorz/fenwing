import io
p='/home/dev/ff/gecko/mozconfig'
s=io.open(p,encoding='utf-8').read()
if 'P23-TRIM' not in s:
    s=s.replace('ac_add_options --enable-optimize','ac_add_options --enable-optimize="-Os"')
    s+='''
# P23-TRIM: size-oriented feature trims (HSP <=200MB goal)
ac_add_options --disable-webrtc
ac_add_options --disable-webcodecs
ac_add_options --disable-webgpu
ac_add_options --disable-accessibility
ac_add_options --disable-parental-controls
ac_add_options --disable-geckodriver
ac_add_options --disable-profiling
ac_add_options --disable-perfetto
'''
    io.open(p,'w',encoding='utf-8').write(s)
print(io.open(p,encoding='utf-8').read())
