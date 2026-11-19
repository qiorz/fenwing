#!/usr/bin/env python3
import io, os

G = '/home/dev/ff/gecko'

# 1) ohos/moz.build
p = G + '/dom/media/platforms/ohos/moz.build'
io.open(p, 'w', encoding='utf-8').write('''# -*- Mode: python; indent-tabs-mode: nil; tab-width: 4 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

UNIFIED_SOURCES += [
    "OHOSDecoderModule.cpp",
    "OHOSVideoDecoder.cpp",
]

FINAL_LIBRARY = "xul"

OS_LIBS += [
    "native_media_codecbase",
    "native_media_core",
    "native_media_vdec",
]
''')
print('ohos moz.build written')

# 2) platforms/moz.build DIRS
p = G + '/dom/media/platforms/moz.build'
s = io.open(p, encoding='utf-8').read()
if 'MOZ_WIDGET_OPENHARMONY' not in s:
    a = 'DIRS += ["agnostic/bytestreams", "agnostic/eme", "agnostic/gmp", "omx"]'
    assert s.count(a) == 1
    s = s.replace(a, a + '''

if CONFIG["MOZ_WIDGET_OPENHARMONY"]:
    DIRS += ["ohos"]
''')
    io.open(p, 'w', encoding='utf-8').write(s)
print('platforms moz.build updated')

# 3) PDMFactory include + registration
p = G + '/dom/media/platforms/PDMFactory.cpp'
s = io.open(p, encoding='utf-8').read()
if 'OHOSDecoderModule' not in s:
    a = '#ifdef MOZ_WIDGET_ANDROID\n#  include "AndroidDecoderModule.h"\n#endif'
    assert s.count(a) == 1
    s = s.replace(a, a + '''
#ifdef MOZ_WIDGET_OPENHARMONY
#  include "ohos/OHOSDecoderModule.h"
#endif''')
    a = '''#ifdef MOZ_WIDGET_ANDROID
    if (StaticPrefs::media_utility_android_media_codec_enabled()) {
      StartupPDM(AndroidDecoderModule::Create(),
                 StaticPrefs::media_android_media_codec_preferred());
    }
#endif'''
    assert s.count(a) == 1
    s = s.replace(a, a + '''
#ifdef MOZ_WIDGET_OPENHARMONY
    StartupPDM(OHOSDecoderModule::Create(), /* aPreferred */ true);
#endif''')
    io.open(p, 'w', encoding='utf-8').write(s)
print('PDMFactory updated')
