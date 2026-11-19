import io
R = '/home/dev/ff/gecko/dom/media/platforms/ohos'
p = R + '/OHOSVideoDecoder.h'
s = io.open(p, encoding='utf-8').read()
if 'mKnowsCompositor' not in s:
    s = s.replace('  layers::ImageContainer* mImageContainer = nullptr;',
                  '  layers::ImageContainer* mImageContainer = nullptr;\n  layers::KnowsCompositor* mKnowsCompositor = nullptr;')
io.open(p, 'w', encoding='utf-8').write(s)

p = R + '/OHOSVideoDecoder.cpp'
s = io.open(p, encoding='utf-8').read()
s = s.replace('      mImageContainer(aParams.mImageContainer),',
              '      mImageContainer(aParams.mImageContainer),\n      mKnowsCompositor(aParams.mKnowsCompositor),')
s = s.replace('      media::TimeUnit::FromMicroseconds(pts), gfx::IntRect(0, 0, w, h),\n      nullptr);',
              '      media::TimeUnit::FromMicroseconds(pts), gfx::IntRect(0, 0, w, h),\n      mKnowsCompositor);')
io.open(p, 'w', encoding='utf-8').write(s)
print('knows compositor wired:', 'mKnowsCompositor' in io.open(p, encoding='utf-8').read())
