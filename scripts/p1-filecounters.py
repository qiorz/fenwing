import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
if 'OHOSStat' not in s:
    s=s.replace('static void OHOSMarker(const char* aMsg) {',
'''static void OHOSStat(const char* aTag, int a, int b, int c) {
  char buf[128];
  snprintf(buf, sizeof(buf), "%s a=%d b=%d c=%d", aTag, a, b, c);
  OHOSMarker(buf);
}
static void OHOSMarker(const char* aMsg) {''')
    # counters
    s=s.replace('  int decNo = sDec.fetch_add(1);',
                '  int decNo = sDec.fetch_add(1);\n  if (decNo % 10 == 0) { OHOSStat("STAT decode", decNo, (int)mFrames.Length(), (int)mFreeInputs.Length()); }')
    s=s.replace('  int n = sNeed.fetch_add(1);',
                '  int n = sNeed.fetch_add(1);\n  if (n % 10 == 0) { OHOSStat("STAT needInput", n, (int)self->mFrames.Length(), (int)self->mFreeInputs.Length()); }')
    s=s.replace('  int outNo = sOut.fetch_add(1);',
                '  int outNo = sOut.fetch_add(1);\n  if (outNo % 10 == 0) { OHOSStat("STAT output", outNo, (int)w, (int)h); }')
io.open(p,'w',encoding='utf-8').write(s)
print('file counters added:', 'OHOSStat' in s)
