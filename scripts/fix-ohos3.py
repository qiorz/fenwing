import io
R='/mnt/d/ff-ohos/work/firefoxport/third_party/gecko/dom/media/platforms/ohos'
p=R+'/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('RefPtr<MediaDataDecoder::ShutdownPromise> OHOSVideoDecoder::Shutdown()',
            'RefPtr<ShutdownPromise> OHOSVideoDecoder::Shutdown()')
s=s.replace('if (!yuv->CopyData(data)) {','if (NS_FAILED(yuv->CopyData(data))) {')
io.open(p,'w',encoding='utf-8').write(s)
print('fixed shutdown/copydata')
