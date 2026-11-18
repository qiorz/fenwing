#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild BrowserPage.ets from pristine sources with the MULTI-SESSION design."""
import io

pristine = '/mnt/d/ff-ohos/refs/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
path = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
src = io.open(pristine, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f'anchor {old[:60]!r} count={src.count(old)}'
    src = src.replace(old, new, count)

# import
rep("import { hilog } from '@kit.PerformanceAnalysisKit';",
    "import { hilog } from '@kit.PerformanceAnalysisKit';\nimport { GeckoViewBoot } from 'gecko';")

# fields + engineReady hack
rep("  @State private currentUrl: string = '';",
    """  @State private currentUrl: string = '';
  @StorageProp('geckoUrl') @Watch('onGeckoUrlChanged') geckoUrl: string = '';
  @StorageProp('geckoSession') geckoSession: string = '';
  @StorageProp('geckoPageLoad') @Watch('onGeckoPageLoadChanged') geckoPageLoad: string = '';
  // ArkTS tabId <-> engine browserIndex (the port's sessionId). Engine browser 0
  // is created by geckoview.js at startup; new tabs start at 1.
  private engineIndexByTab: Map<string, number> = new Map();
  private tabByEngineIndex: Map<number, string> = new Map();
  private nextEngineIndex: number = 1;""")

rep("      this.engineRenderReady = version.availability === EngineAvailability.READY;",
    "      this.engineRenderReady = bridgeReady || version.availability === EngineAvailability.READY;")

# first tab bind
rep("    this.viewModel.createTab(TabViewModel.homeUrl());",
    """    const firstTab = this.viewModel.createTab(TabViewModel.homeUrl());
    // Engine browser 0 is created by geckoview.js at startup with the same URL.
    this.bindEngineSession(firstTab.id, 0);
    this.viewModel.navigate(firstTab.id, 'https://example.com/');
    this.viewModel.markLoaded(firstTab.id, 'Example Domain');""")

# helpers
rep("  private syncTabs(): void {",
    """  private bindEngineSession(tabId: string, engineIndex: number): void {
    this.engineIndexByTab.set(tabId, engineIndex);
    this.tabByEngineIndex.set(engineIndex, tabId);
  }

  private engineIndexOfTab(tabId: string): number | undefined {
    return this.engineIndexByTab.get(tabId);
  }

  private activeEngineIndex(): number | undefined {
    return this.engineIndexOfTab(this.viewModel.getActiveTabId());
  }

  /** Force a repaint after docShellIsActive switch (port needs the toggle). */
  private repaintSoon(): void {
    setTimeout(() => {
      GeckoViewBoot.forceRepaint();
    }, 150);
  }

  /** Engine URL change keeps the address bar and the active tab's URL in sync. */
  private onGeckoUrlChanged(): void {
    if (this.geckoUrl.length === 0) {
      return;
    }
    this.currentUrl = this.geckoUrl;
    hilog.info(DOMAIN, TAG, 'engine url -> %{public}s (session=%{public}s)', this.geckoUrl, this.geckoSession);
  }

  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
  }

  private dismissKeyboard(): void {
    try {
      this.getUIContext().getFocusController().clearFocus();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'clearFocus failed: %{public}s', JSON.stringify(error));
    }
  }

  private syncTabs(): void {""")

# navigate(): per-session load
start = src.index('  private async navigate(input: string): Promise<void> {')
end = src.index('  private titleForUrl(url: string): string {')
new_nav = """  private async navigate(input: string): Promise<void> {
    const resolved: string = TabViewModel.normalizeInput(input, this.searchEngine);
    let tabId: string = this.viewModel.getActiveTabId();
    if (tabId.length === 0) {
      const created = this.viewModel.createTab(resolved);
      tabId = created.id;
      const engineIndex: number = this.nextEngineIndex++;
      this.bindEngineSession(tabId, engineIndex);
      if (this.engineRenderReady) {
        GeckoViewBoot.createSession(engineIndex, resolved);
        GeckoViewBoot.switchToSession(engineIndex);
        this.repaintSoon();
      }
    } else {
      this.viewModel.navigate(tabId, resolved);
    }

    const title: string = this.titleForUrl(resolved);
    if (this.engineRenderReady) {
      try {
        const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
        if (engineIndex !== undefined) {
          GeckoViewBoot.loadUrlForSession(engineIndex, resolved);
        } else {
          GeckoViewBoot.loadUrl(resolved);
        }
      } catch (error) {
        const geckoError: GeckoError = toGeckoError(error as Object);
        this.statusMessage = `loadUrl failed: ${geckoError.code}`;
      }
    } else {
      this.statusMessage = 'Gecko engine not embedded yet (M2/M3).';
    }

    this.viewModel.markLoaded(tabId, title);

    if (!this.privateMode && resolved.startsWith('http')) {
      try {
        const entry = HistoryEntry.create(PROFILE_ID, resolved, title);
        await this.database.addHistory(entry);
        await this.refreshPanels();
      } catch (error) {
        hilog.warn(DOMAIN, TAG, 'history write failed');
      }
    }
    this.syncTabs();
  }

"""
src = src[:start] + new_nav + src[end:]

# TabBar wiring: real multi-session
rep("""        onSelectTab: (tabId: string) => {
          this.viewModel.activateTab(tabId);
        },
        onCloseTab: (tabId: string) => {
          this.viewModel.closeTab(tabId);
        },
        onNewTab: () => {
          this.viewModel.createTab(TabViewModel.newTabUrl());
        }""",
    """        onSelectTab: (tabId: string) => {
          this.viewModel.activateTab(tabId);
          const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
          if (engineIndex !== undefined) {
            GeckoViewBoot.switchToSession(engineIndex);
            this.repaintSoon();
          }
          this.dismissKeyboard();
          this.syncTabs();
        },
        onCloseTab: (tabId: string) => {
          const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
          this.viewModel.closeTab(tabId);
          if (engineIndex !== undefined) {
            GeckoViewBoot.closeSession(engineIndex);
            this.engineIndexByTab.delete(tabId);
            this.tabByEngineIndex.delete(engineIndex);
          }
          const activeIndex: number | undefined = this.activeEngineIndex();
          if (activeIndex !== undefined) {
            GeckoViewBoot.switchToSession(activeIndex);
            this.repaintSoon();
          }
          this.dismissKeyboard();
          this.syncTabs();
        },
        onNewTab: () => {
          const modelUrl: string = TabViewModel.newTabUrl();
          const created = this.viewModel.createTab(modelUrl);
          const engineIndex: number = this.nextEngineIndex++;
          this.bindEngineSession(created.id, engineIndex);
          const engineUrl: string = modelUrl === 'about:newtab' ? 'https://example.org/' : modelUrl;
          GeckoViewBoot.createSession(engineIndex, engineUrl);
          GeckoViewBoot.switchToSession(engineIndex);
          this.repaintSoon();
          this.dismissKeyboard();
          this.syncTabs();
        }""")

io.open(path, 'w', encoding='utf-8').write(src)
print('OK multi-session BrowserPage.ets', len(src), 'chars')
