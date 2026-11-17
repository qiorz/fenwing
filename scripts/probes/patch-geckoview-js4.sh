#!/bin/bash
# patch-geckoview-js4.sh — 让所有 <browser> 绝对定位重叠在窗口上，消除多标签纵向堆叠
set -eu
F=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js
python3 - "$F" <<'PY'
import sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()

old = "    const browser = createBrowser();\n    const isFirst = !this._firstBrowserCreated;"
new = ("    const browser = createBrowser();\n"
       "    const isFirst = !this._firstBrowserCreated;\n"
       "    // ohos: 所有标签的 <browser> 绝对定位重叠在窗口上(否则多标签纵向堆叠),\n"
       "    // 可见性由下面 style.display 控制。\n"
       "    browser.style.position = \"absolute\";\n"
       "    browser.style.left = \"0\";\n"
       "    browser.style.top = \"0\";\n"
       "    browser.style.width = \"100%\";\n"
       "    browser.style.height = \"100%\";")
assert src.count(old) == 1, f"anchor count={src.count(old)}"
src = src.replace(old, new)
open(path, 'w', encoding='utf-8').write(src)
print("patched absolute positioning:", path)
PY
grep -n 'style.position' "$F" | head -3
