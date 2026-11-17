#!/bin/bash
# patch-geckoview-js2.sh — 用内联 style.display 替代 hidden 属性（chrome 窗口无 xul.css）
set -eu
F=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js
python3 - "$F" <<'PY'
import sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()

pairs = [
  ('      browser.setAttribute("hidden", "true");',
   '      browser.style.display = "none";'),
  ('      oldTab.browser.setAttribute("hidden", "true");',
   '      oldTab.browser.style.display = "none";'),
  ('    newTab.browser.removeAttribute("hidden");',
   '    newTab.browser.style.display = "";'),
]
for old, new in pairs:
    assert src.count(old) == 1, f"anchor count={src.count(old)} for {old[:40]}"
    src = src.replace(old, new)
open(path, 'w', encoding='utf-8').write(src)
print("patched style.display:", path)
PY
grep -n 'style.display' "$F" | head -6
