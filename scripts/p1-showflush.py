import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
i=s.find('RefPtr<MediaDataDecoder::FlushPromise> OHOSVideoDecoder::Flush()')
print(s[i:i+900])
