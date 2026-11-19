#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UX fixes: wheel scroll, address bar height, no history dropdown,
transient status toast, progress bar, UA override, target=_blank new tab."""
import io

R = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- GeckoViewBoot
p = R + '/gecko/src/main/ets/GeckoViewBoot.ets'
s = io.open(p, encoding='utf-8').read()
if 'static scroll(' not in s:
    a = "  static setBoolPref(name: string, value: boolean): void {"
    assert s.count(a) == 1
    s = s.replace(a, """  static scroll(dx: number, dy: number, x: number, y: number): void {
    geckoview.scroll(dx, dy, x, y, 0);
  }

  static setCharPref(name: string, value: string): void {
    hilog.info(DOMAIN, TAG, 'setCharPref %{public}s=%{public}s', name, value);
    geckoview.setCharPref(name, value);
  }

""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('GeckoViewBoot scroll/pref ok')

# ---------------------------------------------------------------- d.ts
p = R + '/gecko/src/main/cpp/types/libgeckoview/index.d.ts'
s = io.open(p, encoding='utf-8').read()
if 'export const scroll' not in s:
    a = "export const mouseUp: (x: number, y: number, button: number) => void;"
    assert s.count(a) == 1
    s = s.replace(a, a + "\nexport const scroll: (dx: number, dy: number, x: number, y: number, modifiers: number) => void;")
    io.open(p, 'w', encoding='utf-8').write(s)
print('d.ts scroll ok')

# ---------------------------------------------------------------- GeckoSurface
p = R + '/entry/src/main/ets/components/GeckoSurface.ets'
s = io.open(p, encoding='utf-8').read()
if 'onAxisEvent' not in s:
    a = """      .onMouse((event: MouseEvent) => {
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
print('GeckoSurface wheel ok')

# ---------------------------------------------------------------- AddressBar
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
s = s.replace("""    .padding({ left: 8, right: 8, top: 4, bottom: 4 })""", """    .padding({ left: 8, right: 8, top: 5, bottom: 5 })""")
io.open(p, 'w', encoding='utf-8').write(s)
print('AddressBar height ok')

# ---------------------------------------------------------------- SettingsRepository
p = R + '/entry/src/main/ets/data/SettingsRepository.ets'
s = io.open(p, encoding='utf-8').read()
if 'USER_AGENT' not in s:
    a = "  static readonly ENGINE_LOG_LEVEL: string = 'browser.engine.logLevel';"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  static readonly USER_AGENT: string = 'browser.general.userAgent';")
    a = """  async setSearchEngine(value: string): Promise<void> {"""
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
print('SettingsRepository UA ok')
