import io
p='/home/dev/ff/gecko/dom/media/MediaFormatReader.cpp'
s=io.open(p,encoding='utf-8',errors='replace').read()
if '#include <cstdarg>' not in s:
    s=s.replace('#include <cstdio>','#include <cstdio>\n#include <cstdarg>',1)
io.open(p,'w',encoding='utf-8').write(s)
print('cstdarg ok')
