import io
p='/home/dev/ff/gecko/dom/media/platforms/PDMFactory.cpp'
s=io.open(p,encoding='utf-8').read()
block='''#ifdef MOZ_WIDGET_OPENHARMONY
  {
    FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
    if (f) { fprintf(f, "PDM marker: registering OHOS decoder\\n"); fclose(f); }
  }
  StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
#endif
'''
assert s.count(block)==1
s=s.replace(block,'')
func='RefPtr<PlatformDecoderModule::CreateDecoderPromise> PDMFactory::CreateDecoder('
assert s.count(func)==1
# find opening brace line after signature
idx=s.find(func)
brace=s.find('{', idx)
assert brace>0
lazy='''
#ifdef MOZ_WIDGET_OPENHARMONY
  if (!mOHOSPDMStarted) {
    const auto* vi = aParams.mConfig.GetAsVideoInfo();
    if (vi && (vi->mMimeType.EqualsLiteral("video/avc") ||
               vi->mMimeType.EqualsLiteral("video/hevc"))) {
      mOHOSPDMStarted = true;
      StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
    }
  }
#endif
'''
s=s[:brace+1]+lazy+s[brace+1:]
io.open(p,'w',encoding='utf-8').write(s)
p2='/home/dev/ff/gecko/dom/media/platforms/PDMFactory.h'
s2=io.open(p2,encoding='utf-8').read()
if 'mOHOSPDMStarted' not in s2:
    s2=s2.replace('  bool StartupPDM(already_AddRefed<PlatformDecoderModule> aPDM,',
                  '  bool mOHOSPDMStarted = false;\n  bool StartupPDM(already_AddRefed<PlatformDecoderModule> aPDM,')
io.open(p2,'w',encoding='utf-8').write(s2)
print('lazy registration installed')
