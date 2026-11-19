import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'frame #' not in s:
    s=s.replace('  OHOS_HLOG("decode call size=%{public}d", (int)aSample->Size());',
'''  static std::atomic<int> sDec{0};
  int decNo = sDec.fetch_add(1);
  if (decNo % 30 == 0) { OHOS_HLOG("decode #%{public}d", decNo); }''')
    s=s.replace('  OHOS_HLOG("queued frames=%{public}d", (int)frames.Length());',
'''  static std::atomic<int> sQueued{0};
  int q = sQueued.fetch_add(1);
  if (q % 30 == 0) { OHOS_HLOG("frame #%{public}d queued=%{public}d", q, (int)frames.Length()); }''')
    s=s.replace('  OHOS_HLOG("needInput idx=%{public}d", (int)aIndex);',
'''  static std::atomic<int> sNeed{0};
  int n = sNeed.fetch_add(1);
  if (n % 60 == 0) { OHOS_HLOG("needInput #%{public}d idx=%{public}d", n, (int)aIndex); }''')
io.open(p,'w',encoding='utf-8').write(s)
print('counters every 30/60')
