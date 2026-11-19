import io
R='/mnt/d/ff-ohos/work/firefoxport/third_party/gecko/dom/media/platforms/ohos'
p=R+'/OHOSVideoDecoder.h'
s=io.open(p,encoding='utf-8').read()
if 'NS_INLINE_DECL_THREADSAFE_REFCOUNTING' not in s:
    a='class OHOSVideoDecoder final : public MediaDataDecoder {\n public:'
    assert s.count(a)==1
    s=s.replace(a, a+'\n  NS_INLINE_DECL_THREADSAFE_REFCOUNTING(OHOSVideoDecoder, override)')
    a='  nsCString GetDescriptionName() const override {'
    s=s.replace(a, '  nsCString GetCodecName() const override { return "ohos-hw"_ns; }\n'+a)
io.open(p,'w',encoding='utf-8').write(s)
print('refcount+codecname added')
