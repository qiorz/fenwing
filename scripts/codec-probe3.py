import io

R = '/mnt/d/ff-ohos/work/firefoxport'

p = R + '/gecko/src/main/cpp/CMakeLists.txt'
s = io.open(p, encoding='utf-8').read()
if 'native_media_codecbase' not in s:
    a = '    libhilog_ndk.z.so\n)'
    assert s.count(a) == 1
    s = s.replace(a, '    libhilog_ndk.z.so\n    libnative_media_codecbase.so\n)')
    io.open(p, 'w', encoding='utf-8').write(s)
print('cmake ok')

p = R + '/gecko/src/main/cpp/types/libgecko_napi/index.d.ts'
s = io.open(p, encoding='utf-8').read()
if 'codecProbe' not in s:
    s = s.rstrip() + '\nexport const codecProbe: () => string;\n'
    io.open(p, 'w', encoding='utf-8').write(s)
print('d.ts ok')

p = R + '/gecko/src/main/ets/GeckoEngine.ets'
s = io.open(p, encoding='utf-8').read()
if 'codecProbe' not in s:
    a = '  jitProbe,'
    assert s.count(a) == 1
    s = s.replace(a, '  codecProbe,\n  jitProbe,')
    a = 'export class GeckoEngine {'
    assert s.count(a) == 1
    s = s.replace(a, a + '''
  /** Video decoders reported by OH_AVCodec (JSON array string). */
  static codecProbe(): string {
    try {
      return codecProbe();
    } catch (error) {
      return '[]';
    }
  }
''', 1)
    io.open(p, 'w', encoding='utf-8').write(s)
print('ets ok')
