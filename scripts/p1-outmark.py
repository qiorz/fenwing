import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'decode call' not in s:
    s=s.replace('RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(\n    MediaRawData* aSample) {\n  MutexAutoLock lock(mMutex);',
                'RefPtr<MediaDataDecoder::DecodePromise> OHOSVideoDecoder::Decode(\n    MediaRawData* aSample) {\n  OHOS_HLOG("decode call size=%d", (int)aSample->Size());\n  MutexAutoLock lock(mMutex);')
    s=s.replace('  uint8_t* addr = gApi.bufAddr(aBuffer);\n  const int32_t w = mSize.width;',
                '  static int sOutCount = 0;\n  uint8_t* addr = gApi.bufAddr(aBuffer);\n  const int32_t w = mSize.width;\n  if (sOutCount == 0) { OHOS_HLOG("first output w=%d h=%d", w, h); }\n  sOutCount++;\n  if (sOutCount % 30 == 1) { OHOS_HLOG("output #%d", sOutCount); }')
io.open(p,'w',encoding='utf-8').write(s)
print('decode/output markers', 'decode call' in s)
