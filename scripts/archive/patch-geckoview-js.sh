#!/bin/bash
# patch-geckoview-js.sh — 给移植层 TabManager 打"隐藏非活跃 browser"补丁
# 原因：geckoview.js 把所有 <browser> 都 append 到同一个 <window>，切换只改
# docShellIsActive，多个 browser 同时参与布局 → 画面叠加/串台。XUL 上给非活跃
# browser 加 hidden 属性即可让它退出布局。
set -eu
F=/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js
python3 - "$F" <<'PY'
import sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()

# 1) 后台标签创建时隐藏
old1 = "    const browser = createBrowser();\n    const isFirst = !this._firstBrowserCreated;"
new1 = ("    const browser = createBrowser();\n"
        "    const isFirst = !this._firstBrowserCreated;\n"
        "    // ohos: 非活跃标签不参与窗口布局(否则多个 <browser> 会叠画)\n"
        "    if (!isFirst) {\n"
        "      browser.setAttribute(\"hidden\", \"true\");\n"
        "    }")
assert src.count(old1) == 1, f"anchor1 count={src.count(old1)}"
src = src.replace(old1, new1)

# 2) 切换时隐藏旧标签、显示新标签
old2 = ("      oldTab.browser.preserveLayers(true);\n"
        "      oldTab.browser.docShellIsActive = false;")
new2 = ("      oldTab.browser.preserveLayers(true);\n"
        "      oldTab.browser.docShellIsActive = false;\n"
        "      oldTab.browser.setAttribute(\"hidden\", \"true\");")
assert src.count(old2) >= 1, f"anchor2 count={src.count(old2)}"
src = src.replace(old2, new2, 1)

old3 = ("    newTab.browser.docShellIsActive = true;\n"
        "    this._selectedSessionId = aSessionId;")
new3 = ("    newTab.browser.docShellIsActive = true;\n"
        "    newTab.browser.removeAttribute(\"hidden\");\n"
        "    this._selectedSessionId = aSessionId;")
assert src.count(old3) == 1, f"anchor3 count={src.count(old3)}"
src = src.replace(old3, new3)

open(path, 'w', encoding='utf-8').write(src)
print("patched:", path)
PY
grep -n 'hidden' "$F" | head -10
