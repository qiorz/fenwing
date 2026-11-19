#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visible progress bar + draggable overlay scrollbar."""
import io

R = '/mnt/d/ff-ohos/work/firefoxport'

# ---- geckoview.js: report scroll position ----
p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s = io.open(p, encoding='utf-8').read()
if '__ohosScrollHooked' not in s:
    a = """    const w = aBrowser.contentWindow;
    if (w && !w.__ohosOpenHooked) {"""
    assert s.count(a) == 1
    s = s.replace(a, """    const w0 = aBrowser.contentWindow;
    if (w0 && !w0.__ohosScrollHooked) {
      w0.__ohosScrollHooked = true;
      let last = 0;
      const report = () => {
        try {
          const win = aBrowser.contentWindow;
          const doc = aBrowser.contentDocument;
          if (!win || !doc) {
            return;
          }
          const y = win.scrollY || doc.documentElement.scrollTop || 0;
          const max = Math.max(0, (doc.documentElement.scrollHeight || 0) - (win.innerHeight || 0));
          Services.obs.notifyObservers(null, "airweb-tab-state",
            JSON.stringify({ session: "__scroll__", title: "", url: JSON.stringify({ y: y, max: max }) }));
        } catch (e) {}
      };
      w0.addEventListener("scroll", () => {
        const now = Date.now();
        if (now - last > 120) {
          last = now;
          report();
        }
      }, { passive: true });
      report();
    }
    const w = aBrowser.contentWindow;
    if (w && !w.__ohosOpenHooked) {""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('scroll reporter ok')

# ---- BrowserPage ----
p = R + '/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f'{old[:60]!r} count={s.count(old)}'
    s = s.replace(old, new, n)

# fields
rep("  @State private uaMode: string = 'harmony';",
    """  @State private uaMode: string = 'harmony';
  @State private scrollBarVisible: boolean = false;
  @State private scrollY: number = 0;
  @State private scrollMax: number = 0;
  private scrollHideTimer: number = -1;
  private scrollPanLast: number = 0;""")

# envelope handling
rep("""      if (event.session === '__opentab__') {""",
    """      if (event.session === '__scroll__') {
        try {
          const info: ScrollInfo = JSON.parse(event.url) as ScrollInfo;
          this.scrollY = info.y;
          this.scrollMax = info.max;
          this.scrollBarVisible = info.max > 0;
          if (this.scrollHideTimer >= 0) {
            clearTimeout(this.scrollHideTimer);
          }
          this.scrollHideTimer = setTimeout(() => {
            this.scrollBarVisible = false;
            this.scrollHideTimer = -1;
          }, 1500);
        } catch (error) {
        }
        return;
      }
      if (event.session === '__opentab__') {""")

# progress bar: custom visible bar
rep("""      if (this.loading) {
        Progress({ value: this.geckoProgress, total: 100, type: ProgressType.Linear })
          .width('100%')
          .height(3)
          .color('#4C6FFF')
          .backgroundColor('#12121A')
      }""",
    """      if (this.loading) {
        Stack({ alignContent: Alignment.Start }) {
          Row()
            .width('100%')
            .height(4)
            .backgroundColor('#2A2A3A')
          Row()
            .width(`${Math.max(6, this.geckoProgress)}%`)
            .height(4)
            .backgroundColor('#4C6FFF')
            .borderRadius(2)
        }
        .width('100%')
        .height(4)
      }""")

# scrollbar overlay before loadError block
rep("        if (this.loadError.length > 0) {",
    """        if (this.scrollBarVisible && this.scrollMax > 0 && this.contentHeight > 0) {
          Column() {
            Blank()
              .layoutWeight(Math.max(0.001, this.scrollMax > 0 ? this.scrollY / this.scrollMax : 0))
            Row()
              .width(6)
              .height(Math.max(40, Math.min(this.contentHeight * 0.6,
                this.contentHeight * this.contentHeight / (this.scrollMax + this.contentHeight))))
              .backgroundColor('#88A8C8FF')
              .borderRadius(3)
              .gesture(
                PanGesture()
                  .onActionStart(() => {
                    this.scrollPanLast = 0;
                  })
                  .onActionUpdate((event: GestureEvent) => {
                    const delta: number = event.offsetY - this.scrollPanLast;
                    this.scrollPanLast = event.offsetY;
                    GeckoViewBoot.scroll(0, delta * 3, this.contentWidth / 2, this.contentHeight / 2);
                  })
              )
            Blank()
              .layoutWeight(Math.max(0.001, this.scrollMax > 0 ? 1 - this.scrollY / this.scrollMax : 1))
          }
          .width('100%')
          .height('100%')
          .alignItems(HorizontalAlign.End)
          .hitTestBehavior(HitTestMode.Transparent)
        }

        if (this.loadError.length > 0) {""")

# ScrollInfo interface
if 'interface ScrollInfo' not in s:
    s = s.rstrip() + """

interface ScrollInfo {
  y: number;
  max: number;
}
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('progress+scrollbar ok')
