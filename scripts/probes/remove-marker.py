#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove the PATCH_RAN marker from geckoview.js."""
import io

p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
src = io.open(p, encoding='utf-8').read()
marker = ("    // MARKER: 行为标记，用于验证 patch 是否执行\n"
          "    if (aSessionId !== \"0\") {\n"
          "      aInitialUrl = \"data:text/html,<h1 style='font-size:80px;color:red'>PATCH_RAN</h1>\";\n"
          "    }\n")
assert src.count(marker) == 1, src.count(marker)
src = src.replace(marker, "")
io.open(p, 'w', encoding='utf-8').write(src)
print('marker removed')
