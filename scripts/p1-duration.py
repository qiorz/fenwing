import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
old='''  auto result = VideoData::CreateAndCopyData(
      mInfo, mImageContainer, 0, media::TimeUnit::FromMicroseconds(pts),
      media::TimeUnit::FromMicroseconds(pts), buffer, true,
      media::TimeUnit::FromMicroseconds(pts), gfx::IntRect(0, 0, w, h),
      nullptr);'''
assert s.count(old)==1
new='''  const int64_t frameDur = mInfo.mRate > 0 ? (int64_t)(1000000 / mInfo.mRate) : 33333;
  auto result = VideoData::CreateAndCopyData(
      mInfo, mImageContainer, 0, media::TimeUnit::FromMicroseconds(pts),
      media::TimeUnit::FromMicroseconds(frameDur), buffer, true,
      media::TimeUnit::FromMicroseconds(pts), gfx::IntRect(0, 0, w, h),
      nullptr);'''
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('frame duration fixed')
