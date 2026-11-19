import io
p='/home/dev/ff/gecko/dom/media/platforms/PDMFactory.cpp'
s=io.open(p,encoding='utf-8').read()
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
assert s.count(lazy)==1
s=s.replace(lazy,'')
anchor='''#ifdef MOZ_WIDGET_ANDROID
  if (StaticPrefs::media_android_media_codec_enabled()) {
    StartupPDM(AndroidDecoderModule::Create(),
               StaticPrefs::media_android_media_codec_preferred());
  }
#endif

  StartupPDM(AgnosticDecoderModule::Create(),'''
assert s.count(anchor)==1
new='''#ifdef MOZ_WIDGET_ANDROID
  if (StaticPrefs::media_android_media_codec_enabled()) {
    StartupPDM(AndroidDecoderModule::Create(),
               StaticPrefs::media_android_media_codec_preferred());
  }
#endif
#ifdef MOZ_WIDGET_OPENHARMONY
  StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
#endif

  StartupPDM(AgnosticDecoderModule::Create(),'''
s=s.replace(anchor,new)
io.open(p,'w',encoding='utf-8').write(s)
print('registration moved back to startup')
