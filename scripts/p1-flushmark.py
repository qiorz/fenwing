import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'FLUSH' not in s:
    s=s.replace('RefPtr<MediaDataDecoder::FlushPromise> OHOSVideoDecoder::Flush() {\n  MutexAutoLock lock(mMutex);',
                'RefPtr<MediaDataDecoder::FlushPromise> OHOSVideoDecoder::Flush() {\n  MutexAutoLock lock(mMutex);\n  OHOSPtrTag("FLUSH", this, (int)mFrames.Length(), 0);')
io.open(p,'w',encoding='utf-8').write(s)
print('flush marker:', 'FLUSH' in s)
