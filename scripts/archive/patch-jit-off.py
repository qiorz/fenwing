#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Disable JIT again (interpreter fallback, works without ACL)."""
import io
import shutil

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# 1) module.json5: drop kernel permissions
p = ROOT + '/entry/src/main/module.json5'
src = io.open(p, encoding='utf-8').read()
if 'ALLOW_WRITABLE_CODE_MEMORY' in src:
    src = src.replace("""      },
      {
        "name": "ohos.permission.kernel.ALLOW_WRITABLE_CODE_MEMORY"
      },
      {
        "name": "ohos.permission.kernel.DISABLE_CODE_MEMORY_PROTECTION"
      }
    ],""", """      }
    ],""")
    io.open(p, 'w', encoding='utf-8').write(src)
print('module.json5: kernel permissions removed')

# 2) restore interpreter-only flag
p = ROOT + '/gecko/src/main/ets/GeckoViewBoot.ets'
src = io.open(p, encoding='utf-8').read()
a = "      // ACL granted: let XPCOMInit's RWX probe enable the full JIT backend.\n      commandlineArgs: '',"
assert src.count(a) == 1, src.count(a)
src = src.replace(a, "      commandlineArgs: '--airweb-force-no-jit',")
io.open(p, 'w', encoding='utf-8').write(src)
print('GeckoViewBoot: force-no-jit restored')

# 3) restore plain libxul without .permission section
src_lib = '/mnt/d/ff-ohos/artifacts/gecko/libxul-stripped.so'
dst_lib = ROOT + '/gecko/libs/arm64-v8a/libxul.so'
shutil.copyfile(src_lib, dst_lib)
print('staged plain libxul.so ->', dst_lib)
