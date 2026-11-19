#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UX fixes part 3: progress/toast/UA wiring/no-history + new-tab interceptor."""
import io

R = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------- BrowserPage ----------------
p = R + '/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f'{old[:60]!r} count={s.count(old)}'
    s = s.replace(old, new, n)

# progress prop
if 'geckoProgress' not in s:
    rep("  @StorageProp('geckoMenuSeq')", "  @StorageProp('geckoProgress') geckoProgress: number = 0;\n  @StorageProp('geckoMenuSeq')")

# status auto-hide
rep("  @State private statusMessage: string = '';",
    "  @State @Watch('onStatusMessageChanged') private statusMessage: string = '';\n  private statusHideTimer: number = -1;")

# disable history suggestions
rep("  private onAddressInput(text: string): void {\n    if (text.length === 0) {",
    "  private onAddressInput(text: string): void {\n    this.showSuggestions = false;\n    return;\n    if (text.length === 0) {")

# progress bar + status method: insert status method before onMenuEvent
rep("  private onMenuEvent(): void {",
    """  private onStatusMessageChanged(): void {
    if (this.statusHideTimer >= 0) {
      clearTimeout(this.statusHideTimer);
      this.statusHideTimer = -1;
    }
    if (this.statusMessage.length > 0) {
      this.statusHideTimer = setTimeout(() => {
        this.statusMessage = '';
        this.statusHideTimer = -1;
      }, 3000);
    }
  }

  private applyUserAgent(): void {
    let ua: string = '';
    if (this.uaMode === 'windows') {
      ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
    } else if (this.uaMode === 'mobile') {
      ua = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36';
    } else {
      ua = 'Mozilla/5.0 (Linux; HarmonyOS 5.0; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
    }
    try {
      GeckoViewBoot.setCharPref('general.useragent.override', ua);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'ua apply failed');
    }
  }

  private setUaMode(mode: string): void {
    this.uaMode = mode;
    this.settings.setUserAgentMode(mode).catch((error: Object) => {
      hilog.warn(DOMAIN, TAG, 'ua persist failed');
    });
    this.applyUserAgent();
  }

  private onMenuEvent(): void {""")

# UA state field
rep("  @State private uaMode: string = 'harmony';" if '@State private uaMode' in s else "  @State private showSuggestions: boolean = false;",
    "  @State private uaMode: string = 'harmony';\n  @State private showSuggestions: boolean = false;")

# load UA from settings
rep("    this.searchEngine = this.settings.getSearchEngine();",
    "    this.searchEngine = this.settings.getSearchEngine();\n    this.uaMode = this.settings.getUserAgentMode();")

# apply UA after engine ready (bootstrap)
rep("    if (this.debugCtxMenu) {",
    "    this.applyUserAgent();\n    if (this.debugCtxMenu) {")

# progress bar UI before suggestions block
rep("      if (this.showSuggestions && this.suggestions.length > 0) {",
    """      if (this.loading) {
        Progress({ value: this.geckoProgress, total: 100, type: ProgressType.Linear })
          .width('100%')
          .height(3)
          .color('#4C6FFF')
          .backgroundColor('#12121A')
      }

      if (this.showSuggestions && this.suggestions.length > 0) {""")

# SettingsView props
rep("            engineLabel: this.engineLabel,",
    "            engineLabel: this.engineLabel,\n            uaMode: this.uaMode,")
rep("""            onTogglePrivateByDefault: (enabled: boolean) => {
              this.privateByDefault = enabled;
              this.settings.setPrivateByDefault(enabled);
            },""",
    """            onTogglePrivateByDefault: (enabled: boolean) => {
              this.privateByDefault = enabled;
              this.settings.setPrivateByDefault(enabled);
            },
            onUaModeChange: (mode: string) => {
              this.setUaMode(mode);
            },""")

io.open(p, 'w', encoding='utf-8').write(s)
print('BrowserPage ok')

# ---------------- SettingsView ----------------
p = R + '/entry/src/main/ets/views/SettingsView.ets'
s = io.open(p, encoding='utf-8').read()
if 'uaMode' not in s:
    a = "  @Prop engineLabel: string = '';"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  @Prop uaMode: string = 'harmony';")
    a = "  onOpenDiagnostics: () => void = () => {\n  };"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  onUaModeChange: (mode: string) => void = () => {\n  };")
    a = "        this.toggleRow('默认隐私模式', '新标签不写历史与记录', this.privateByDefault, 'private')"
    assert s.count(a) == 1
    s = s.replace(a, a + """

        Text('兼容性（浏览器标识）')
          .fontSize(12)
          .fontColor('#8A8AA3')
          .width('100%')
          .margin({ top: 6 })
        Row({ space: 8 }) {
          this.uaButton('HarmonyOS', 'harmony')
          this.uaButton('移动版', 'mobile')
          this.uaButton('Windows', 'windows')
        }
        .width('100%')
        Text('部分网站会按 UA 判断设备；遇到排版/功能异常可切换。')
          .fontSize(11)
          .fontColor('#7C7C96')
          .width('100%')""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('SettingsView ok')
