#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

R = '/mnt/d/ff-ohos/work/firefoxport'
p = R + '/gecko/src/main/cpp/src/gecko_module.cpp'
s = io.open(p, encoding='utf-8').read()

if 'CodecProbe' not in s:
    a = '#include <hilog/log.h>'
    assert s.count(a) == 1
    s = s.replace(a, a + '\n#include <multimedia/player_framework/native_avcapability.h>')

    fn = '''namespace gecko {

// Lists video decoders reported by OH_AVCodec and whether each is hardware.
napi_value CodecProbe(napi_env env, napi_callback_info info) {
    uint32_t count = 0;
    OH_AVCapability** list = OH_AVCodec_GetCapabilityList(OH_AVCODEC_TYPE_VIDEO_DECODER, &count);
    std::string json = "[";
    if (list != nullptr) {
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
            json += name != nullptr ? name : "";
            json += "\\",\\"mime\\":\\"";
            json += mime != nullptr ? mime : "";
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

}  // namespace gecko

'''
    a = '// ---------------------------------------------------------------------------\n// Module registration'
    assert s.count(a) == 1
    s = s.replace(a, fn + a)

    a = '        {"jitProbe", nullptr, JitProbe, nullptr, nullptr, nullptr, napi_default, nullptr},'
    assert s.count(a) == 1
    s = s.replace(a, a + '\n        {"codecProbe", nullptr, CodecProbe, nullptr, nullptr, nullptr, napi_default, nullptr},')
    io.open(p, 'w', encoding='utf-8').write(s)
print('cpp ok')

p = R + '/gecko/src/main/cpp/CMakeLists.txt'
s = io.open(p, encoding='utf-8').read()
if 'native_media_codecbase' not in s:
    a = 'target_link_libraries(gecko_napi'
    assert s.count(a) == 1
    s = s.replace(a, a + '\n    native_media_codecbase')
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
