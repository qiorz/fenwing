#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply tab-integration edits to the pristine BrowserPage.ets (UTF-8 safe)."""
import io, sys

path = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
src = io.open(path, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f'anchor {old[:60]!r} count={src.count(old)}'
    src = src.replace(old, new, count)

# A. import
rep("import { hilog } from '@kit.PerformanceAnalysisKit';",
    "import { hilog } from '@kit.PerformanceAnalysisKit';\nimport { GeckoViewBoot } from 'gecko';")

# B. start page constant
rep("const PANEL_SETTINGS: string = 'settings';",
    """const PANEL_SETTINGS: string = 'settings';

/**
 * Self-drawn new-tab placeholder for the engine (the geckoview build has no
 * about:newtab content). Kept as a data: URL so it needs no network.
 */
const START_PAGE_HTML: string = 'data:text/html,' + encodeURIComponent(
  '<html><body style="margin:0;background:#101014;color:#E6E6F0;' +
  'font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh">' +
  '<div style="text-align:center">' +
  '<h1 style="font-size:44px;margin:0;color:#FF7139">Firefox for HarmonyOS</h1>' +
  '<p style="font-size:20px;color:#B0B0C8">Gecko engine inside an ArkTS shell</p>' +
  '<p style="font-size:16px;color:#7C7C96">Type a URL in the address bar above to start browsing.</p>' +
  '</div></body></html>');""")

# C. fields
rep("  @State private currentUrl: string = '';",
    """  @State private currentUrl: string = '';
  @StorageProp('geckoUrl') @Watch('onGeckoUrlChanged') geckoUrl: string = '';
  @StorageProp('geckoSession') geckoSession: string = '';
  @StorageProp('geckoPageLoad') @Watch('onGeckoPageLoadChanged') geckoPageLoad: string = '';
  // ArkTS tabId <-> engine browser index. The shell currently keeps ONE live
  // engine browser (index 0) and restores each tab by URL, because the port's
  // multi-<browser> window does not repaint correctly on switch.
  private engineIndexByTab: Map<string, number> = new Map();
  private tabByEngineIndex: Map<number, string> = new Map();
  private engineUrlByTab: Map<string, string> = new Map();""")

# D. first tab binding
rep("    this.viewModel.createTab(TabViewModel.homeUrl());",
    """    const firstTab = this.viewModel.createTab(TabViewModel.homeUrl());
    // Engine browser 0 is created by geckoview.js at startup with the same URL.
    this.bindEngineSession(firstTab.id, 0, 'https://example.com/');
    this.viewModel.navigate(firstTab.id, 'https://example.com/');
    this.viewModel.markLoaded(firstTab.id, 'Example Domain');""")

# E. helpers before syncTabs
rep("  private syncTabs(): void {",
    """  private bindEngineSession(tabId: string, engineIndex: number, engineUrl: string): void {
    this.engineIndexByTab.set(tabId, engineIndex);
    this.tabByEngineIndex.set(engineIndex, tabId);
    if (engineUrl.length > 0) {
      this.engineUrlByTab.set(tabId, engineUrl);
    }
  }

  private engineIndexOfTab(tabId: string): number | undefined {
    return this.engineIndexByTab.get(tabId);
  }

  /** Engine URL change keeps the address bar and the active tab's URL in sync. */
  private onGeckoUrlChanged(): void {
    if (this.geckoUrl.length === 0) {
      return;
    }
    this.currentUrl = this.geckoUrl;
    const activeTabId: string = this.viewModel.getActiveTabId();
    if (activeTabId.length > 0) {
      this.engineUrlByTab.set(activeTabId, this.geckoUrl);
    }
    hilog.info(DOMAIN, TAG, 'engine url -> %{public}s (session=%{public}s)', this.geckoUrl, this.geckoSession);
  }

  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
  }

  /** Hides the soft keyboard when the active tab changes. */
  private dismissKeyboard(): void {
    try {
      this.getUIContext().getFocusController().clearFocus();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'clearFocus failed: %{public}s', JSON.stringify(error));
    }
  }

  private syncTabs(): void {""")

# F. navigate() body: replace from signature to titleForUrl
start = src.index('  private async navigate(input: string): Promise<void> {')
end = src.index('  private titleForUrl(url: string): string {')
new_nav = """  private async navigate(input: string): Promise<void> {
    const resolved: string = TabViewModel.normalizeInput(input, this.searchEngine);
    let tabId: string = this.viewModel.getActiveTabId();
    if (tabId.length === 0) {
      const created = this.viewModel.createTab(resolved);
      tabId = created.id;
      this.bindEngineSession(tabId, 0, resolved);
    } else {
      this.viewModel.navigate(tabId, resolved);
    }

    const title: string = this.titleForUrl(resolved);
    if (this.engineRenderReady) {
      try {
        // One live engine browser: navigation always targets index 0.
        GeckoViewBoot.loadUrlForSession(0, resolved);
        this.engineUrlByTab.set(tabId, resolved);
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

# G. TabBar wiring
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
          // Restore this tab's page in the single live engine browser.
          const engineUrl: string | undefined = this.engineUrlByTab.get(tabId);
          if (engineUrl !== undefined && engineUrl.length > 0) {
            GeckoViewBoot.loadUrlForSession(0, engineUrl);
            GeckoViewBoot.forceRepaint();
          }
          this.dismissKeyboard();
          this.syncTabs();
        },
        onCloseTab: (tabId: string) => {
          this.viewModel.closeTab(tabId);
          this.engineIndexByTab.delete(tabId);
          this.engineUrlByTab.delete(tabId);
          const activeTabId: string = this.viewModel.getActiveTabId();
          const activeUrl: string | undefined = this.engineUrlByTab.get(activeTabId);
          if (activeUrl !== undefined && activeUrl.length > 0) {
            GeckoViewBoot.loadUrlForSession(0, activeUrl);
            GeckoViewBoot.forceRepaint();
          }
          this.dismissKeyboard();
          this.syncTabs();
        },
        onNewTab: () => {
          const modelUrl: string = TabViewModel.newTabUrl();
          const created = this.viewModel.createTab(modelUrl);
          const engineUrl: string = modelUrl === 'about:newtab' ? 'https://example.org/' : modelUrl;
          this.bindEngineSession(created.id, 0, engineUrl);
          GeckoViewBoot.loadUrlForSession(0, engineUrl);
          GeckoViewBoot.forceRepaint();
          this.dismissKeyboard();
          this.syncTabs();
        }""")

io.open(path, 'w', encoding='utf-8').write(src)
print('OK: BrowserPage.ets rewritten', len(src), 'chars')
