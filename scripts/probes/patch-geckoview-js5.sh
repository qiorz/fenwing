#!/bin/bash
# patch-geckoview-js5.sh — 切标签时把旧 browser 从 DOM 摘除、新 browser 重新挂载
set -eu
F=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js
python3 - "$F" <<'PY'
import sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()

anchor = '    newTab.browser.style.display = "";\n    this._selectedSessionId = aSessionId;'
new = ('    newTab.browser.style.display = "";\n'
       '    // ohos: 关键修复 —— 旧 browser 从 DOM 摘除(彻底退出窗口布局/合成)，\n'
       '    // 新 browser 若不在 DOM 中则重新挂载。\n'
       '    if (oldTab && oldTab.browser && oldTab.browser.parentNode) {\n'
       '      oldTab.browser.parentNode.removeChild(oldTab.browser);\n'
       '    }\n'
       '    if (!newTab.browser.parentNode) {\n'
       '      window.document.documentElement.appendChild(newTab.browser);\n'
       '    }\n'
       '    dump(`[OHOS_TAB] switch to ${aSessionId}, detached old browser\\n`);\n'
       '    this._selectedSessionId = aSessionId;')
assert src.count(anchor) == 1, f"anchor count={src.count(anchor)}"
src = src.replace(anchor, new)
open(path, 'w', encoding='utf-8').write(src)
print("patched detach/attach:", path)
PY
grep -n 'OHOS_TAB' "$F" | head -3
