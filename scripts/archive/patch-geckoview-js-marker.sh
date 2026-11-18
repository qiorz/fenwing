#!/bin/bash
# patch-geckoview-js-marker.sh — 行为标记：非首个 session 强制加载 PATCH_RAN 页面
set -eu
F=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js
python3 - "$F" <<'PY'
import sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()
anchor = "  createBrowserForSession(aSessionId, aInitialUrl = null) {\n"
assert src.count(anchor) == 1, src.count(anchor)
insert = anchor + ("    // MARKER: 行为标记，用于验证 patch 是否执行\n"
                   "    if (aSessionId !== \"0\") {\n"
                   "      aInitialUrl = \"data:text/html,<h1 style='font-size:80px;color:red'>PATCH_RAN</h1>\";\n"
                   "    }\n")
src = src.replace(anchor, insert)
open(path, 'w', encoding='utf-8').write(src)
print("marker inserted")
PY
grep -n 'PATCH_RAN' "$F" | head -2
