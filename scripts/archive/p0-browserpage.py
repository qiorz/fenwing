#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0 BrowserPage: session restore + persistence + recovery banner + load-error overlay."""
import io

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f'anchor {old[:60]!r} count={s.count(old)}'
    s = s.replace(old, new, n)

# ---- import
if "from '../service/SessionStore'" not in s:
    rep("import { GeckoViewBoot } from 'gecko';",
        "import { GeckoViewBoot } from 'gecko';\nimport { SavedSession, SessionStore } from '../service/SessionStore';")

# ---- fields
rep("  private nextEngineIndex: number = 1;",
    """  private nextEngineIndex: number = 1;
  @StorageProp('engineUnclean') engineUnclean: boolean = false;
  @State private showRecoveryBanner: boolean = false;
  @State private recoveredCount: number = 0;
  @State private loadError: string = '';
  private loadWatchdog: number = -1;
  private saveTimer: number = -1;
  private store: SessionStore = SessionStore.instance();""")

# ---- bootstrap: restore or default
old_first = """    const firstTab = this.viewModel.createTab(TabViewModel.homeUrl());
    // Engine browser 0 is created by geckoview.js at startup with the same URL.
    this.bindEngineSession(firstTab.id, 0);
    this.pushHistory(firstTab.id, 'https://example.com/');
    this.viewModel.navigate(firstTab.id, 'https://example.com/');
    this.viewModel.markLoaded(firstTab.id, 'Example Domain');"""
assert s.count(old_first) == 1, s.count(old_first)
s = s.replace(old_first, """    const saved: SavedSession | undefined = this.store.load();
    if (saved !== undefined && saved.tabs.length > 0) {
      this.restoreSession(saved);
      if (this.engineUnclean) {
        this.recoveredCount = saved.tabs.length;
        this.showRecoveryBanner = true;
        hilog.warn(DOMAIN, TAG, 'unclean exit detected, restored %{public}d tabs', saved.tabs.length);
      } else {
        hilog.info(DOMAIN, TAG, 'session restored (%{public}d tabs)', saved.tabs.length);
      }
    } else {
      const firstTab = this.viewModel.createTab(TabViewModel.homeUrl());
      // Engine browser 0 is created by geckoview.js at startup with the same URL.
      this.bindEngineSession(firstTab.id, 0);
      this.pushHistory(firstTab.id, 'https://example.com/');
      this.viewModel.navigate(firstTab.id, 'https://example.com/');
      this.viewModel.markLoaded(firstTab.id, 'Example Domain');
    }""")

# ---- helpers: restore / save / watchdog / retry (insert before refreshPanels)
anchor = "  private async refreshPanels(): Promise<void> {"
assert s.count(anchor) == 1
helpers = """  /** Recreates ArkTS tabs and engine sessions from a persisted snapshot. */
  private restoreSession(saved: SavedSession): void {
    const restoredIds: Array<string> = [];
    for (let i = 0; i < saved.tabs.length; i++) {
      const tab = saved.tabs[i];
      const created = this.viewModel.createTab(tab.url.length > 0 ? tab.url : TabViewModel.homeUrl());
      const engineIndex: number = i === 0 ? 0 : this.nextEngineIndex++;
      this.bindEngineSession(created.id, engineIndex);
      this.pushHistory(created.id, tab.url);
      this.viewModel.markLoaded(created.id, tab.title);
      restoredIds.push(created.id);
      if (engineIndex > 0) {
        GeckoViewBoot.createSession(engineIndex, tab.url);
      }
    }
    const activeIndex: number = Math.min(Math.max(saved.activeIndex, 0), restoredIds.length - 1);
    this.viewModel.activateTab(restoredIds[activeIndex]);
    if (activeIndex > 0) {
      GeckoViewBoot.switchToSession(activeIndex);
    } else {
      GeckoViewBoot.loadUrlForSession(0, saved.tabs[0].url);
    }
    GeckoViewBoot.forceRepaint();
    this.syncTabs();
  }

  private scheduleSessionSave(): void {
    if (this.saveTimer >= 0) {
      clearTimeout(this.saveTimer);
    }
    this.saveTimer = setTimeout(() => {
      this.persistSession();
    }, 400);
  }

  private persistSession(): void {
    try {
      const models = this.viewModel.snapshot();
      if (models.length === 0) {
        return;
      }
      const session = new SavedSession();
      session.tabs = new Array<SavedTab>();
      let activeIndex: number = 0;
      const activeId: string = this.viewModel.getActiveTabId();
      for (let i = 0; i < models.length; i++) {
        const tab = new SavedTab();
        tab.url = models[i].url;
        tab.title = models[i].title;
        session.tabs.push(tab);
        if (models[i].id === activeId) {
          activeIndex = i;
        }
      }
      session.activeIndex = activeIndex;
      this.store.save(session);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'persistSession failed: %{public}s', JSON.stringify(error));
    }
  }

  private startLoadWatchdog(): void {
    this.stopLoadWatchdog();
    this.loadWatchdog = setTimeout(() => {
      if (this.loading) {
        this.loadError = '页面加载超时：请检查网络连接，或重试。';
        hilog.warn(DOMAIN, TAG, 'load watchdog fired');
      }
    }, 20000);
  }

  private stopLoadWatchdog(): void {
    if (this.loadWatchdog >= 0) {
      clearTimeout(this.loadWatchdog);
      this.loadWatchdog = -1;
    }
  }

  private retryLoad(): void {
    this.loadError = '';
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex !== undefined) {
      GeckoViewBoot.reloadForSession(engineIndex);
      this.repaintSoon();
    }
  }

  private goHome(): void {
    this.loadError = '';
    this.navigate('https://example.com/');
  }

  private async refreshPanels(): Promise<void> {"""
s = s.replace(anchor, helpers)

# ---- syncTabs persists
rep("""    } else {
      this.currentUrl = '';
      this.currentTitle = '新标签页';
      this.loading = false;
    }
  }""",
    """    } else {
      this.currentUrl = '';
      this.currentTitle = '新标签页';
      this.loading = false;
    }
    this.scheduleSessionSave();
  }""")

# ---- page load watchdog hooks
rep("""  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
    if (this.geckoPageLoad === 'stop') {
      this.refreshHistoryState();
    }
  }""",
    """  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
    if (this.loading) {
      this.loadError = '';
      this.startLoadWatchdog();
    } else {
      this.stopLoadWatchdog();
      this.refreshHistoryState();
    }
  }""")

# ---- UI: recovery banner
rep("""  build() {
    Column() {
      AddressBar({""",
    """  build() {
    Column() {
      if (this.showRecoveryBanner) {
        Row({ space: 8 }) {
          Text(`检测到上次异常退出，已自动恢复 ${this.recoveredCount} 个标签`)
            .fontSize(12)
            .fontColor('#F2D9A0')
            .layoutWeight(1)
          Button('知道了')
            .fontSize(12)
            .height(28)
            .backgroundColor('#3A3220')
            .fontColor('#F2D9A0')
            .onClick(() => {
              this.showRecoveryBanner = false;
            })
        }
        .width('100%')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#2A2418')
      }

      AddressBar({""")

# ---- UI: load error overlay inside content stack
rep("""        if (!this.engineRenderReady) {
          this.placeholderContent()
        }
      }
      .width('100%')
      .layoutWeight(1)""",
    """        if (!this.engineRenderReady) {
          this.placeholderContent()
        }
        if (this.loadError.length > 0) {
          Column({ space: 14 }) {
            Text('页面加载失败')
              .fontSize(18)
              .fontWeight(FontWeight.Medium)
              .fontColor('#E6E6F0')
            Text(this.loadError)
              .fontSize(13)
              .fontColor('#A0A0B8')
              .textAlign(TextAlign.Center)
              .maxLines(3)
            Row({ space: 12 }) {
              Button('重试')
                .fontSize(14)
                .backgroundColor('#4C6FFF')
                .fontColor('#FFFFFF')
                .onClick(() => {
                  this.retryLoad();
                })
              Button('回到首页')
                .fontSize(14)
                .backgroundColor('#2A2A3A')
                .fontColor('#E6E6F0')
                .onClick(() => {
                  this.goHome();
                })
            }
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
          .padding(24)
          .backgroundColor('#F2101014')
        }
      }
      .width('100%')
      .layoutWeight(1)""")

io.open(p, 'w', encoding='utf-8').write(s)
print('BrowserPage P0 patched, len', len(s))
