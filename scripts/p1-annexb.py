import io
R='/mnt/d/ff-ohos/work/firefoxport/third_party/gecko/dom/media/platforms/ohos'
p=R+'/OHOSVideoDecoder.h'
s=io.open(p,encoding='utf-8').read()
if 'NeedsConversion' not in s:
    s=s.replace('  nsCString GetCodecName() const override { return "ohos-hw"_ns; }',
'''  nsCString GetCodecName() const override { return "ohos-hw"_ns; }
  ConversionRequired NeedsConversion() const override {
    return ConversionRequired::kNeedAnnexB;
  }''')
io.open(p,'w',encoding='utf-8').write(s)
print('NeedsConversion added')
