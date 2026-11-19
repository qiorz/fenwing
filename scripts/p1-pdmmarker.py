import io
p='/home/dev/ff/gecko/dom/media/platforms/PDMFactory.cpp'
s=io.open(p,encoding='utf-8').read()
if 'PDM marker' not in s:
    s=s.replace('#ifdef MOZ_WIDGET_OPENHARMONY\n    StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);\n#endif',
'''#ifdef MOZ_WIDGET_OPENHARMONY
    {
      FILE* f = fopen("/data/storage/el2/base/haps/entry/files/ohosdec.log", "a");
      if (f) { fprintf(f, "PDM marker: registering OHOS decoder\\n"); fclose(f); }
    }
    StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
#endif''')
    io.open(p,'w',encoding='utf-8').write(s)
print('pdm marker added')
