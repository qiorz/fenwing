#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove the DOM detach/attach block from geckoview.js (display:none is enough now)."""
import io

p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
src = io.open(p, encoding='utf-8').read()
block = ("    // ohos: 关键修复 —— 旧 browser 从 DOM 摘除(彻底退出窗口布局/合成)，\n"
         "    // 新 browser 若不在 DOM 中则重新挂载。\n"
         "    if (oldTab && oldTab.browser && oldTab.browser.parentNode) {\n"
         "      oldTab.browser.parentNode.removeChild(oldTab.browser);\n"
         "    }\n"
         "    if (!newTab.browser.parentNode) {\n"
         "      window.document.documentElement.appendChild(newTab.browser);\n"
         "    }\n"
         "    dump(`[OHOS_TAB] switch to ${aSessionId}, detached old browser\\n`);\n")
assert src.count(block) == 1, src.count(block)
src = src.replace(block, "")
io.open(p, 'w', encoding='utf-8').write(src)
print('detach block removed')
