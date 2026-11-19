import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'FRAME0' not in s:
    s=s.replace('  RefPtr<VideoData> video = result.unwrap();\n  if (!video) {',
'''  RefPtr<VideoData> video = result.unwrap();
  if (!video) {''')
    s=s.replace('  RefPtr<VideoData> video = result.unwrap();',
'''  RefPtr<VideoData> video = result.unwrap();
  {
    static int sFirst = 0;
    if (sFirst < 1) {
      sFirst++;
      int size = video->mImage ? (int)video->mImage->GetSize().width : -1;
      uint64_t sum = 0;
      for (int i = 0; i < 4096 && i < (int)ySize; i++) { sum += y[i]; }
      char msg[96];
      snprintf(msg, sizeof(msg), "FRAME0 imgw=%d yw=%d sum4k=%llu",
               size, (int)w, (unsigned long long)sum);
      OHOSMarker(msg);
    }
  }''')
    s=s.replace('  OHOS_HLOG("needInput resolve frames=%{public}d", (int)ready.Length());',
                '  OHOS_HLOG("needInput resolve frames=%{public}d", (int)ready.Length());\n    if (ready.Length() > 0) { OHOSMarker("RESOLVE_FRAMES"); }')
io.open(p,'w',encoding='utf-8').write(s)
print('frame0 diagnostics added')
