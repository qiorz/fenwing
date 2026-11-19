#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UX fixes part 2 (wheel wiring, height, toast, progress, UA, new tab)."""
import io

R = '/mnt/d/ff-ohos/work/firefoxport'

# 1) wheel onAxisEvent
p = R + '/entry/src/main/ets/components/GeckoSurface.ets'
s = io.open(p, encoding='utf-8').read()
if 'onAxisEvent' not in s:
    a = """        .onMouse((event: MouseEvent) => {
          this.handleMouse(event);
        })"""
    assert s.count(a) == 1
    s = s.replace(a, a + """
        .onAxisEvent((event: AxisEvent) => {
          const dx: number = event.axisHorizontal;
          const dy: number = event.axisVertical;
          if (Math.abs(dx) > 0.001 || Math.abs(dy) > 0.001) {
            GeckoViewBoot.scroll(dx, dy, event.x * this.scaleX(), event.y * this.scaleY());
          }
        })""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('wheel ok')

# 2) AddressBar height
p = R + '/entry/src/main/ets/components/AddressBar.ets'
s = io.open(p, encoding='utf-8').read()
s = s.replace("""        .borderRadius(6)
        .height(30)
        .layoutWeight(1)""", """        .borderRadius(6)
        .height(36)
        .fontSize(14)
        .layoutWeight(1)""")
s = s.replace("""        .fontSize(12)
        .height(30)
        .width(64)""", """        .fontSize(12)
        .height(36)
        .width(64)""")
io.open(p, 'w', encoding='utf-8').write(s)
print('addressbar ok')

# 3) SettingsRepository UA
p = R + '/entry/src/main/ets/data/SettingsRepository.ets'
s = io.open(p, encoding='utf-8').read()
if 'USER_AGENT' not in s:
    a = "  static readonly ENGINE_LOG_LEVEL: string = 'browser.engine.logLevel';"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  static readonly USER_AGENT: string = 'browser.general.userAgent';")
    a = "  async setSearchEngine(value: string): Promise<void> {"
    assert s.count(a) == 1
    s = s.replace(a, """  getUserAgentMode(): string {
    return this.requireStore().getSync(SettingsKeys.USER_AGENT, 'harmony') as string;
  }

  async setUserAgentMode(value: string): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.USER_AGENT, value);
    await store.flush();
  }

""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('settings repo ok')
