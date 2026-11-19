import io
p='/home/dev/ff/gecko/dom/media/MediaFormatReader.cpp'
s=io.open(p,encoding='utf-8',errors='replace').read()
for kw in ['OnVideoDecoded','VideoDecoded','DecodeVideo','mVideo.mOutput']:
    idx=s.find(kw)
    print(kw, idx)
