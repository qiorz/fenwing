import io
p = '/home/dev/ff/gecko/mozconfig'
s = io.open(p, encoding='utf-8').read()
# keep a copy of the attempted config for the record
io.open('/home/dev/ff/gecko/mozconfig.p23-trim', 'w', encoding='utf-8').write(s)
# revert to the stable configuration that produced the current 250MB HSP
lines = []
for line in s.splitlines():
    if 'P23-TRIM' in line:
        break
    lines.append(line.replace('--enable-optimize="-Os"', '--enable-optimize'))
out = '\n'.join(lines).rstrip() + '\n'
io.open(p, 'w', encoding='utf-8').write(out)
print(out)
