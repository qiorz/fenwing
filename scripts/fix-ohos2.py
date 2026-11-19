import io
R='/mnt/d/ff-ohos/work/firefoxport/third_party/gecko/dom/media/platforms/ohos'
p=R+'/OHOSDecoderModule.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('media::MediaDecodeSupport::kHardware','media::DecodeSupport::HardwareDecode')
io.open(p,'w',encoding='utf-8').write(s)
p=R+'/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('#include "mozilla/layers/ImageContainer.h"','#include "ImageContainer.h"')
io.open(p,'w',encoding='utf-8').write(s)
print('fixed enums and include')
