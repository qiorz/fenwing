import io,re
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp'
s=io.open(p,encoding='utf-8').read()
block_start=s.find('static void MPtrTag')
block_end=s.find('}', s.find('fclose(f);', block_start))+1
if block_start>0:
    block=s[block_start:block_end+1]
    # remove second occurrence
    first=s.find('static void MPtrTag')
    second=s.find('static void MPtrTag', first+1)
    if second>0:
        end2=s.find('}', s.find('fclose(f);', second))+1
        s=s[:second]+s[end2+1:]
io.open(p,'w',encoding='utf-8').write(s)
print('duplicates:', s.count('static void MPtrTag'))
