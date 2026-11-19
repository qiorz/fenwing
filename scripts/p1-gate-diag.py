import io
# decoder helpers: gate on env
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSVideoDecoder.cpp'
s=io.open(p,encoding='utf-8').read()
for fn in ['static void OHOSMarker(const char* aMsg) {','static void OHOSStatGlobal(const char* aTag, int a, int b, int c) {','static void OHOSPtrTag(const char* aTag, void* p, int a, int b) {']:
    if fn in s and 'OHOS_DIAG_LOG' not in s.split(fn)[1][:200]:
        s=s.replace(fn, fn+'\n  if (!getenv("OHOS_DIAG_LOG")) { return; }',1)
io.open(p,'w',encoding='utf-8').write(s)
print('decoder gated:', s.count('OHOS_DIAG_LOG'))

# reader helper gate
p2='/home/dev/ff/gecko/dom/media/MediaFormatReader.cpp'
s2=io.open(p2,encoding='utf-8').read()
if 'OHOS_DIAG_LOG' not in s2:
    s2=s2.replace('static void READERLOG(const char* aFmt, ...) {',
                  'static void READERLOG(const char* aFmt, ...) {\n  if (!getenv("OHOS_DIAG_LOG")) { return; }')
io.open(p2,'w',encoding='utf-8').write(s2)
print('reader gated:', s2.count('OHOS_DIAG_LOG'))

# sm helper gate
p3='/home/dev/ff/gecko/dom/media/MediaDecoderStateMachine.cpp'
s3=io.open(p3,encoding='utf-8').read()
if 'OHOS_DIAG_LOG' not in s3:
    s3=s3.replace('    if (sP) { sP(0, 4, 0, "OHOSSM", __VA_ARGS__); }',
                  '    if (sP && getenv("OHOS_DIAG_LOG")) { sP(0, 4, 0, "OHOSSM", __VA_ARGS__); }')
io.open(p3,'w',encoding='utf-8').write(s3)
print('sm gated:', s3.count('OHOS_DIAG_LOG'))
