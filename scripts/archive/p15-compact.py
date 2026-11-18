#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1.5: compact chrome + native menu overlay (context/app menus)."""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- GeckoViewBoot
p = ROOT + '/gecko/src/main/ets/GeckoViewBoot.ets'
s = io.open(p, encoding='utf-8').read()

if 'registerMenu' not in s:
    a = "  onFullscreen?: (fullscreen: boolean) => void;"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  onMenu?: (json: string) => void;")

    a = "\n      if (handlers.onDownload !== undefined) {\n        geckoview.registerDownloadCallback"
    assert s.count(a) == 1
    s = s.replace(a, """\n      if (handlers.onMenu !== undefined) {
        geckoview.registerMenuCallback((json: string) => {
          if (handlers.onMenu !== undefined) {
            handlers.onMenu(json);
          }
        });
      }
      if (handlers.onDownload !== undefined) {\n        geckoview.registerDownloadCallback
        geckoview.registerMenuCallback((json: string) => {
          if (handlers.onMenu !== undefined) {
            handlers.onMenu(json);
          }
        });
      }
""" + a)

    a = """  static resolveFilePicker(callbackId: number, result: number, path: string): void {"""
    assert s.count(a) == 1
    s = s.replace(a, """  static resolveMenuCommand(menuId: number, itemId: number, modifiers: number): void {
    hilog.info(DOMAIN, TAG, 'resolveMenuCommand menu=%{public}d item=%{public}d', menuId, itemId);
    geckoview.resolveMenuCommand(menuId, itemId, modifiers);
  }

  static closeNativeMenu(menuId: number): void {
    hilog.info(DOMAIN, TAG, 'closeNativeMenu menu=%{public}d', menuId);
    geckoview.closeNativeMenu(menuId);
  }

""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('GeckoViewBoot menu ok')

# ---------------------------------------------------------------- d.ts
p = ROOT + '/gecko/src/main/cpp/types/libgeckoview/index.d.ts'
s = io.open(p, encoding='utf-8').read()
if 'registerMenuCallback' not in s:
    a = "export const registerTabStateCallback: (callback: (json: string) => void) => void;"
    assert s.count(a) == 1
    s = s.replace(a, a + """
export const registerMenuCallback: (callback: (json: string) => void) => void;
export const resolveMenuCommand: (menuId: number, itemId: number, modifiers: number) => void;
export const closeNativeMenu: (menuId: number) => void;""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('d.ts menu ok')

# ---------------------------------------------------------------- AddressBar compact
p = ROOT + '/entry/src/main/ets/components/AddressBar.ets'
s = io.open(p, encoding='utf-8').read()
s = s.replace("""      .borderRadius(8)
      .width(36)
      .height(36)
      .enabled(enabled)""", """      .borderRadius(6)
      .width(30)
      .height(30)
      .enabled(enabled)""")
s = s.replace("""        .borderRadius(8)
        .width(36)
        .height(36)
        .enabled(this.canGoBack)""", """        .borderRadius(6)
        .width(30)
        .height(30)
        .enabled(this.canGoBack)""")
s = s.replace("""        .borderRadius(8)
        .width(36)
        .height(36)
        .enabled(this.canGoForward)""", """        .borderRadius(6)
        .width(30)
        .height(30)
        .enabled(this.canGoForward)""")
# input compact
s = s.replace("""        .borderRadius(8)
        .height(36)
        .layoutWeight(1)""", """        .borderRadius(6)
        .height(30)
        .layoutWeight(1)""")
# remove private badge block
s = s.replace("""      if (this.privateMode) {
        Text('私密')
          .fontSize(11)
          .fontColor('#C9A7FF')
          .padding({ left: 8, right: 8, top: 4, bottom: 4 })
          .backgroundColor('#2A1F3A')
          .borderRadius(6)
      }

""", "")
# navigate button compact
s = s.replace("""      Button('前往')
        .fontSize(13)
        .height(36)
        .backgroundColor('#4C6FFF')
        .fontColor('#FFFFFF')
        .borderRadius(8)""", """      Button('前往')
        .fontSize(12)
        .height(30)
        .width(52)
        .backgroundColor('#4C6FFF')
        .fontColor('#FFFFFF')
        .borderRadius(6)""")
s = s.replace("""    .padding({ left: 12, right: 12, top: 8, bottom: 8 })""", """    .padding({ left: 8, right: 8, top: 4, bottom: 4 })""")
io.open(p, 'w', encoding='utf-8').write(s)
print('AddressBar compacted')

# ---------------------------------------------------------------- TabBar compact + menu button
p = ROOT + '/entry/src/main/ets/components/TabBar.ets'
s = io.open(p, encoding='utf-8').read()
if 'onMenu' not in s:
    a = "  onNewTab: () => void = () => {\n  };"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  onMenu: () => void = () => {\n  };")
    s = s.replace("""            .width(168)
            .padding({ left: 10, right: 8, top: 7, bottom: 7 })""", """            .width(150)
            .padding({ left: 8, right: 6, top: 4, bottom: 4 })""")
    s = s.replace("""      .height(40)""", """      .height(32)""")
    s = s.replace("""      Button('+')
        .fontSize(18)
        .width(36)
        .height(36)""", """      Button('+')
        .fontSize(16)
        .width(30)
        .height(30)""")
    s = s.replace("""        .onClick(() => {
          this.onNewTab();
        })
    }
    .width('100%')
    .padding({ left: 12, right: 12, top: 6, bottom: 8 })""", """        .onClick(() => {
          this.onNewTab();
        })
      Button('☰')
        .fontSize(16)
        .width(30)
        .height(30)
        .fontColor('#E6E6F0')
        .backgroundColor('#1C1C26')
        .borderRadius(6)
        .onClick(() => {
          this.onMenu();
        })
    }
    .width('100%')
    .padding({ left: 8, right: 8, top: 4, bottom: 4 })""")
    s = s.replace("""              Text(this.titleOf(chip))
                .fontSize(12)""", """              Text(this.titleOf(chip))
                .fontSize(11)""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('TabBar compacted')
