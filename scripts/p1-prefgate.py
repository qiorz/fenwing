import io
p='/home/dev/ff/gecko/dom/media/platforms/PDMFactory.cpp'
s=io.open(p,encoding='utf-8').read()
old='''#ifdef MOZ_WIDGET_OPENHARMONY
  // TEMP diagnostic: set OHOS_SOFT=1 in environment to disable HW decode.
  const char* sSoft = getenv("OHOS_SOFT");
  if (!(sSoft && *sSoft == '1')) {
    StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
  }
#endif'''
assert s.count(old)==1
new='''#ifdef MOZ_WIDGET_OPENHARMONY
  if (Preferences::GetBool("media.ohos.hw_decode", true)) {
    StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
  }
#endif'''
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('pref gate installed')
