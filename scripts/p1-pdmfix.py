import io
p='/home/dev/ff/gecko/dom/media/platforms/PDMFactory.cpp'
s=io.open(p,encoding='utf-8').read()
util='''#ifdef MOZ_WIDGET_OPENHARMONY
    {
      FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
      if (f) { fprintf(f, "PDM marker: registering OHOS decoder\\n"); fclose(f); }
    }
    StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
#endif
'''
assert s.count(util)==1
s=s.replace(util,'')
defaults='''#ifdef MOZ_WIDGET_ANDROID
  if (StaticPrefs::media_android_media_codec_enabled()) {
    StartupPDM(AndroidDecoderModule::Create(),
               StaticPrefs::media_android_media_codec_preferred());
  }
#endif

  StartupPDM(AgnosticDecoderModule::Create(),'''
assert s.count(defaults)==1
new='''#ifdef MOZ_WIDGET_ANDROID
  if (StaticPrefs::media_android_media_codec_enabled()) {
    StartupPDM(AndroidDecoderModule::Create(),
               StaticPrefs::media_android_media_codec_preferred());
  }
#endif
#ifdef MOZ_WIDGET_OPENHARMONY
  {
    FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
    if (f) { fprintf(f, "PDM marker: registering OHOS decoder\\n"); fclose(f); }
  }
  StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
#endif

  StartupPDM(AgnosticDecoderModule::Create(),'''
s=s.replace(defaults,new)
io.open(p,'w',encoding='utf-8').write(s)
print('registration moved to CreateDefaultPDMs')
