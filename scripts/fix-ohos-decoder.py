import io

R = '/mnt/d/ff-ohos/work/firefoxport/third_party/gecko/dom/media/platforms/ohos'

p = R + '/OHOSVideoDecoder.h'
s = io.open(p, encoding='utf-8').read()
s = s.replace('class ImageContainer;\n', 'namespace layers {\nclass ImageContainer;\n}  // namespace layers\n')
s = s.replace('RefPtr<ImageContainer> mImageContainer;', 'layers::ImageContainer* mImageContainer = nullptr;')
io.open(p, 'w', encoding='utf-8').write(s)

p = R + '/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()
s = s.replace('RefPtr<ShutdownPromise> OHOSVideoDecoder::Shutdown()',
              'RefPtr<MediaDataDecoder::ShutdownPromise> OHOSVideoDecoder::Shutdown()')
s = s.replace('RefPtr<Image> image = mImageContainer->CreatePlanarYCbCrImage();',
              'RefPtr<layers::Image> image = mImageContainer->CreatePlanarYCbCrImage();')
s = s.replace('PlanarYCbCrData data;', 'layers::PlanarYCbCrData data;')
s = s.replace("""  data.mPicX = 0;
  data.mPicY = 0;
  data.mPicSize = gfx::IntSize(w, h);
  data.mYChannel = addr;
  data.mYSize = gfx::IntSize(w, h);
  data.mYStride = w;
  data.mCbCrStride = w;
  data.mCbCrSize = gfx::IntSize(w / 2, h / 2);
  data.mCbChannel = addr + (w * h);
  data.mCrChannel = nullptr;
  data.mColorDepth = ColorDepth::COLOR_8;
  data.mYUVColorSpace = YUVColorSpace::BT709;
  data.mColorRange = ColorRange::LIMITED;""",
"""  data.mYChannel = addr;
  data.mYStride = w;
  data.mCbChannel = addr + (w * h);
  data.mCrChannel = nullptr;
  data.mCbCrStride = w;
  data.mPictureRect = gfx::IntRect(0, 0, w, h);
  data.mChromaSubsampling = gfx::ChromaSubsampling::HALF_WIDTH_AND_HEIGHT;
  data.mColorDepth = gfx::ColorDepth::COLOR_8;
  data.mYUVColorSpace = gfx::YUVColorSpace::BT709;
  data.mColorRange = gfx::ColorRange::LIMITED;""")
s = s.replace('TimeUnit::FromMicroseconds', 'media::TimeUnit::FromMicroseconds')
s = s.replace('#include "ImageContainer.h"', '#include "mozilla/layers/ImageContainer.h"')
io.open(p, 'w', encoding='utf-8').write(s)

p = R + '/OHOSDecoderModule.h'
s = io.open(p, encoding='utf-8').read()
s = s.replace('class OHOSDecoderModule : public PlatformDecoderModule {\n public:',
              'class OHOSDecoderModule : public PlatformDecoderModule {\n public:\n  OHOSDecoderModule() = default;\n')
s = s.replace(' private:\n  OHOSDecoderModule() = default;\n  ~OHOSDecoderModule() = default;',
              ' private:\n  ~OHOSDecoderModule() = default;')
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
