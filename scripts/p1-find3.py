import io,re
p='/home/dev/ff/gecko/dom/media/MediaFormatReader.cpp'
s=io.open(p,encoding='utf-8',errors='replace').read()
for kw in ['ReturnOutput(','mDecoder->Decode','Decode(']:
    print('--',kw)
    for m in re.finditer(re.escape(kw), s):
        line=s.count('\n',0,m.start())+1
        print(line)
