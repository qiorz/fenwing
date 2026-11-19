import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
i=s.find('RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(')
print(s[i:i+1400])
