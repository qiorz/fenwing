import io
p = '/home/dev/ff/gecko/mozconfig'
s = io.open(p, encoding='utf-8').read()
s = s.replace('ac_add_options --disable-perfetto\n', '')
io.open(p, 'w', encoding='utf-8').write(s)
print(s)
