import io
p='/home/dev/ff/gecko/dom/media/MediaFormatReader.cpp'
s=io.open(p,encoding='utf-8',errors='replace').read()
import re
for kw in ['OnDecoded','Decode(']:
    for m in re.finditer(re.escape(kw), s):
        i=m.start()
        line=s.count('\n',0,i)+1
        print(kw, line)
