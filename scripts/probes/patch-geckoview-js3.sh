#!/bin/bash
# patch-geckoview-js3.sh — 背景标签不再 preserveLayers，避免旧标签图层残留叠画
set -eu
F=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js
python3 - "$F" <<'PY'
import sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()

pairs = [
  # 后台新建标签
  ('      browser.docShellIsActive = false;\n      browser.preserveLayers(true);',
   '      browser.docShellIsActive = false;\n      browser.preserveLayers(false);'),
  # 切换走的旧标签
  ('      oldTab.browser.preserveLayers(true);\n      oldTab.browser.docShellIsActive = false;',
   '      oldTab.browser.preserveLayers(false);\n      oldTab.browser.docShellIsActive = false;'),
]
for old, new in pairs:
    assert src.count(old) == 1, f"anchor count={src.count(old)} for {old[:50]!r}"
    src = src.replace(old, new)
open(path, 'w', encoding='utf-8').write(src)
print("patched preserveLayers:", path)
PY
grep -n 'preserveLayers' "$F" | head -8
