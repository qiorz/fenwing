#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add a video-decoder capability probe NAPI (OH_AVCodec) and log it at startup."""
import io

R = '/mnt/d/ff-ohos/work/firefoxport'

# 1) C++ probe
p = R + '/gecko/src/main/cpp/src/gecko_module.cpp'
s = io.open(p, encoding='utf-8').read()
if 'codecProbe' not in s:
    inc = '#include <multimedia/player_framework/native_avcapability.h>\n'
    anchor = '#include "napi/native_api.h"'
    assert s.count(anchor) == 1
    s = s.replace(anchor, inc + anchor)
    fn = '''
// P4: video decoder capability probe (OH_AVCodec capability API).
static napi_value CodecProbe(napi_env env, napi_callback_info info) {
  uint32_t count = 0;
  OH_AVCapability** list =
      OH_AVCodec_GetCapabilityList(OH_AVCODEC_TYPE_VIDEO_DECODER, &count);
  std::string json = "[";
  if (list != nullptr && count > 0) {
    for (uint32_t i = 0; i < count; i++) {
      OH_AVCapability* cap = list[i];
      if (cap == nullptr) {
        continue;
      }
      const char* name = OH_AVCapability_GetName(cap);
      const char* mime = OH_AVCapability_GetMimeType(cap);
      bool hw = OH_AVCapability_IsHardware(cap);
      int32_t inst = OH_AVCapability_GetMaxSupportedInstances(cap);
      if (i > 0) {
        json += ",";
      }
      json += "{\\"name\\":\\"";
      json += name ? name : "";
      json += "\\",\\"mime\\":\\"";
      json += mime ? mime : "";
      json += "\\",\\"hw\\":";
      json += hw ? "true" : "false";
      json += ",\\"maxInstances\\":";
      json += std::to_string(inst);
      json += "}";
    }
  }
  json += "]";
  napi_value out;
  napi_create_string_utf8(env, json.c_str(), NAPI_AUTO_LENGTH, &out);
  return out;
}

'''
    anchor = 'napi_value JitProbe('
    if anchor in s:
        s = s.replace(anchor, fn + anchor, 1)
    else:
        anchor2 = 'static napi_value Init(napi_env env, napi_value exports)'
        assert s.count(anchor2) == 1
        s = s.replace(anchor2, fn + anchor2, 1)
    # register
    anchor3 = 'ExportFunction('
    reg = '    ExportFunction("codecProbe", CodecProbe);\n'
    s = s.replace('    ExportFunction("jitProbe", JitProbe);\n',
                  '    ExportFunction("jitProbe", JitProbe);\n' + reg)
    io.open(p, 'w', encoding='utf-8').write(s)
print('codec probe cpp added' if 'codecProbe' in io.open(p, encoding='utf-8').read() else 'FAILED')

# 2) CMake link
p = R + '/gecko/src/main/cpp/CMakeLists.txt'
s = io.open(p, encoding='utf-8').read()
if 'native_media_codecbase' not in s:
    a = 'target_link_libraries(gecko_napi'
    assert s.count(a) == 1
    s = s.replace(a, a + '\n    native_media_codecbase')
    io.open(p, 'w', encoding='utf-8').write(s)
print('cmake link added')

# 3) d.ts
p = R + '/gecko/src/main/cpp/types/libgecko_napi/index.d.ts'
s = io.open(p, encoding='utf-8').read()
if 'codecProbe' not in s:
    s = s.rstrip() + '\nexport const codecProbe: () => string;\n'
    io.open(p, 'w', encoding='utf-8').write(s)
print('d.ts ok')

# 4) GeckoEngine wrapper
p = R + '/gecko/src/main/ets/GeckoEngine.ets'
s = io.open(p, encoding='utf-8').read()
if 'codecProbe' not in s:
    a = 'export class GeckoEngine {'
    assert s.count(a) == 1
    s = s.replace(a, a + '''
  /** Lists hardware/software video decoders reported by OH_AVCodec. */
  static codecProbe(): string {
    try {
      return geckoNapi.codecProbe();
    } catch (error) {
      return '[]';
    }
  }
''', 1)
    io.open(p, 'w', encoding='utf-8').write(s)
print('engine wrapper ok')
