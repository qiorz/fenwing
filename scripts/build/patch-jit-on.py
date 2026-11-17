#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enable JIT: declare kernel permissions + drop the interpreter-only flag.
Run only when the signing profile (ACL) actually grants these permissions,
otherwise installation fails ("permission not in profile")."""
import io
import shutil

ROOT = '/mnt/d/ff-ohos/work/firefoxport'
PERMS = [
    'ohos.permission.kernel.ALLOW_WRITABLE_CODE_MEMORY',
    'ohos.permission.kernel.DISABLE_CODE_MEMORY_PROTECTION',
]

# 1) module.json5 requestPermissions
p = ROOT + '/entry/src/main/module.json5'
src = io.open(p, encoding='utf-8').read()
if 'ALLOW_WRITABLE_CODE_MEMORY' not in src:
    anchor = """    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      }
    ],"""
    assert src.count(anchor) == 1, src.count(anchor)
    blocks = ',\n'.join(
        '      {\n'
        f'        "name": "{name}"\n'
        '      }' for name in PERMS)
    src = src.replace(anchor, """    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      },
""" + blocks + """
    ],""")
    io.open(p, 'w', encoding='utf-8').write(src)
print('module.json5: kernel permissions declared')

# 2) engine decides JIT by itself (no force-no-jit)
p = ROOT + '/gecko/src/main/ets/GeckoViewBoot.ets'
src = io.open(p, encoding='utf-8').read()
a = "      commandlineArgs: '--airweb-force-no-jit',"
assert src.count(a) == 1
src = src.replace(a, "      // ACL granted: let XPCOMInit's RWX probe enable the full JIT backend.\n      commandlineArgs: '',")
io.open(p, 'w', encoding='utf-8').write(src)
print('GeckoViewBoot: force-no-jit removed')

# 3) staged libxul with .permission section
src_lib = '/mnt/d/ff-ohos/artifacts/gecko/libxul-jit.so'
dst_lib = ROOT + '/gecko/libs/arm64-v8a/libxul.so'
shutil.copyfile(src_lib, dst_lib)
print('staged libxul.so with .permission section ->', dst_lib)
