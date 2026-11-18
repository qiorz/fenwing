#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real context menu: pref + minimal contentAreaContextMenu popup in geckoview.js."""
import io

# ---------------------------------------------------------------- geckoview.js
p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s = io.open(p, encoding='utf-8').read()

if 'ohosOpenContextMenu' not in s:
    helper = """
// ohos: 最小内容区右键/长按菜单(交给 OHOSMenuBridge → ArkTS 浮层)
// 触发条件: popup id = contentAreaContextMenu + openPopupAtScreen(...,isContextMenu=true)
// + pref ohos.menu.native_overlay=true
function ohosOpenContextMenu(aBrowser, aX, aY) {
  try {
    let popup = document.getElementById("ohos-content-context-menu");
    if (!popup) {
      popup = document.createXULElement("menupopup");
      popup.id = "contentAreaContextMenu";
      popup.setAttribute("type", "content");
      const mk = (label, accel, fn) => {
        const mi = document.createXULElement("menuitem");
        mi.setAttribute("label", label);
        if (accel) {
          mi.setAttribute("acceltext", accel);
        }
        mi.addEventListener("command", fn);
        popup.appendChild(mi);
      };
      mk("刷新页面", "Ctrl+R", () => { try { aBrowser.reload(); } catch (e) {} });
      mk("后退", "Alt+Left", () => { try { aBrowser.browsingContext.goBack(); } catch (e) {} });
      mk("前进", "Alt+Right", () => { try { aBrowser.browsingContext.goForward(); } catch (e) {} });
      const sep = document.createXULElement("menuseparator");
      popup.appendChild(sep);
      mk("复制页面地址", "", () => {});
      document.documentElement.appendChild(popup);
    }
    popup.openPopupAtScreen(aX, aY, true);
    dump(`[OHOS_CTX] open at ${aX},${aY}\\n`);
  } catch (e) {
    dump(`[OHOS_CTX] failed: ${e}\\n`);
  }
}

function startup() {"""
    assert s.count('\nfunction startup() {') == 1
    s = s.replace('\nfunction startup() {', helper, 1)

    # attach listener in createBrowserForSession right after browser creation
    anchor = "    const browser = createBrowser();\n"
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + """    browser.addEventListener("contextmenu", function (ev) {
      try {
        ev.preventDefault();
        ohosOpenContextMenu(browser, ev.screenX, ev.screenY);
      } catch (e) {
        dump(`[OHOS_CTX] listener failed: ${e}\\n`);
      }
    }, true);
""", 1)
    io.open(p, 'w', encoding='utf-8').write(s)
print('geckoview.js context menu added')

# ---------------------------------------------------------------- GeckoViewBoot
p = '/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s = io.open(p, encoding='utf-8').read()
if 'setBoolPref' not in s:
    a = "  static setFullZoom(zoom: number): void {"
    assert s.count(a) == 1
    s = s.replace(a, """  static setBoolPref(name: string, value: boolean): void {
    hilog.info(DOMAIN, TAG, 'setBoolPref %{public}s=%{public}s', name, `${value}`);
    geckoview.setBoolPref(name, value);
  }

""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('GeckoViewBoot setBoolPref ok')

# ---------------------------------------------------------------- EntryAbility
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()
if 'native_overlay' not in s:
    a = "      const engineArgs: string = nojit ? '--airweb-force-no-jit' : '';"
    assert s.count(a) == 1
    s = s.replace(a, a + """
      // Enable the port's native-menu overlay path once XPCOM/prefs are ready.
      setTimeout(() => {
        try {
          GeckoViewBoot.setBoolPref('ohos.menu.native_overlay', true);
          hilog.info(DOMAIN, 'GeckoBoot', 'native menu pref enabled');
        } catch (menuPrefError) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'native menu pref failed');
        }
      }, 3000);""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('EntryAbility pref enable ok')
