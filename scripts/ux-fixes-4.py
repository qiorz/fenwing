#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UX fixes part 4: uaButton builder, new-tab interceptor, demo blank link."""
import io

R = '/mnt/d/ff-ohos/work/firefoxport'

# uaButton builder
p = R + '/entry/src/main/ets/views/SettingsView.ets'
s = io.open(p, encoding='utf-8').read()
if 'uaButton' in s and '@Builder\n  uaButton' not in s:
    a = "  build() {"
    assert s.count(a) == 1
    s = s.replace(a, """  @Builder
  uaButton(label: string, mode: string) {
    Button(label)
      .fontSize(12)
      .height(32)
      .layoutWeight(1)
      .backgroundColor(this.uaMode === mode ? '#2A3550' : '#17171F')
      .fontColor(this.uaMode === mode ? '#CFE0FF' : '#A0A0B8')
      .borderRadius(6)
      .onClick(() => {
        this.onUaModeChange(mode);
      })
  }

  build() {""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('uaButton ok')

# geckoview.js new-tab interception
p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s = io.open(p, encoding='utf-8').read()
if 'ohosInstallNewTabHooks' not in s:
    a = "function ohosClipboardWrite(aText) {"
    assert s.count(a) == 1
    s = s.replace(a, """function ohosOpenNewTab(aUrl) {
  try {
    if (!aUrl) {
      return;
    }
    Services.obs.notifyObservers(null, "airweb-tab-state",
      JSON.stringify({ session: "__opentab__", title: "", url: String(aUrl) }));
  } catch (e) {}
}

function ohosInstallNewTabHooks(aBrowser) {
  try {
    const doc = aBrowser.contentDocument;
    if (!doc || doc.__ohosNewTabHooked) {
      return;
    }
    doc.__ohosNewTabHooked = true;
    doc.addEventListener("click", (ev) => {
      try {
        if (ev.button !== 0) {
          return;
        }
        const a = ev.target && ev.target.closest ? ev.target.closest("a[href]") : null;
        if (a && (a.target === "_blank" || a.getAttribute("target") === "_blank")) {
          ev.preventDefault();
          ev.stopPropagation();
          ohosOpenNewTab(a.href);
        }
      } catch (e) {}
    }, true);
    const w = aBrowser.contentWindow;
    if (w && !w.__ohosOpenHooked) {
      w.__ohosOpenHooked = true;
      w.open = function (url) {
        if (url) {
          ohosOpenNewTab(url);
        }
        return null;
      };
    }
  } catch (e) {}
}

function ohosClipboardWrite(aText) {""")
    a = "    browser.addEventListener(\"contextmenu\", function (ev) {"
    assert s.count(a) == 1
    s = s.replace(a, """    browser.addEventListener("pageshow", function () {
      ohosInstallNewTabHooks(browser);
    }, true);
    browser.addEventListener("load", function () {
      ohosInstallNewTabHooks(browser);
    }, true);
""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('geckoview hooks ok')

# demo blank-target link
p = R + '/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()
if 'target="_blank"' not in s:
    a = '<p><a href="https://example.com/">示例链接</a></p>'
    assert s.count(a) == 1
    s = s.replace(a, a + '<p><a href="https://example.com/?blank=1" target="_blank">新标签链接</a></p>')
    io.open(p, 'w', encoding='utf-8').write(s)
print('demo link ok')
