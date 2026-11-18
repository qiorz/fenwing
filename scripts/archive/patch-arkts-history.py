#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ArkTS-side per-tab navigation history (back/forward), independent of the
port's getSessionHistory NAPI which is not available at runtime."""
import io

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
src = io.open(p, encoding='utf-8').read()

# fields
anchor = "  @State private canGoBack: boolean = false;"
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + """
  @State private canGoForward: boolean = false;
  // Per-tab URL stacks used for back/forward (the port's session-history NAPI
  // is not available at runtime, so the shell tracks navigation itself).
  private tabHistory: Map<string, Array<string>> = new Map();
  private tabHistoryIndex: Map<string, number> = new Map();
  private suppressHistoryPush: boolean = false;""")

# replace refreshHistoryState body
old_refresh_start = src.index('  private refreshHistoryState(): void {')
old_refresh_end = src.index('\n  private back(): void {', old_refresh_start)
new_refresh = """  /** Recomputed canGoBack/canGoForward from the ArkTS-side history stacks. */
  private refreshHistoryState(): void {
    const tabId: string = this.viewModel.getActiveTabId();
    const urls: Array<string> | undefined = this.tabHistory.get(tabId);
    const index: number = this.tabHistoryIndex.get(tabId) ?? 0;
    const count: number = urls !== undefined ? urls.length : 0;
    this.canGoBack = count > 0 && index > 0;
    this.canGoForward = count > 0 && index + 1 < count;
    hilog.info(DOMAIN, TAG, 'history index=%{public}d count=%{public}d back=%{public}s fwd=%{public}s',
      index, count, `${this.canGoBack}`, `${this.canGoForward}`);
  }

  /** Records a committed navigation for the tab (dedupes consecutive URLs). */
  private pushHistory(tabId: string, url: string): void {
    if (url.length === 0 || this.suppressHistoryPush) {
      return;
    }
    let urls: Array<string> | undefined = this.tabHistory.get(tabId);
    if (urls === undefined) {
      urls = new Array<string>();
      this.tabHistory.set(tabId, urls);
    }
    let index: number = this.tabHistoryIndex.get(tabId) ?? -1;
    if (index >= 0 && index < urls.length && urls[index] === url) {
      return;
    }
    while (urls.length > index + 1) {
      urls.pop();
    }
    urls.push(url);
    this.tabHistoryIndex.set(tabId, urls.length - 1);
    this.refreshHistoryState();
  }

  /** Loads a history entry and updates the cursor without re-pushing it. */
  private loadHistoryEntry(tabId: string, entryIndex: number): void {
    const urls: Array<string> | undefined = this.tabHistory.get(tabId);
    if (urls === undefined || entryIndex < 0 || entryIndex >= urls.length) {
      return;
    }
    const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
    if (engineIndex === undefined) {
      return;
    }
    this.suppressHistoryPush = true;
    this.tabHistoryIndex.set(tabId, entryIndex);
    const url: string = urls[entryIndex];
    try {
      GeckoViewBoot.loadUrlForSession(engineIndex, url);
      this.repaintSoon();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'history load failed: %{public}s', JSON.stringify(error));
    }
    setTimeout(() => {
      this.suppressHistoryPush = false;
      this.refreshHistoryState();
    }, 900);
    this.refreshHistoryState();
  }"""
src = src[:old_refresh_start] + new_refresh + src[old_refresh_end:]

# rewrite back()/forward() to use history stacks
def replace_method(src, name, new_body):
    start = src.index(f'  private {name}(): void {{')
    end = src.index('\n  private ', start + 10)
    # find the closing of method by matching the next '\n  }\n' after start
    close = src.index('\n  }\n', start) + len('\n  }\n')
    return src[:start] + new_body + src[close:]

back_body = """  private back(): void {
    const tabId: string = this.viewModel.getActiveTabId();
    const index: number = this.tabHistoryIndex.get(tabId) ?? 0;
    if (index <= 0) {
      return;
    }
    this.loadHistoryEntry(tabId, index - 1);
    this.syncTabs();
  }
"""
fwd_body = """  private forward(): void {
    const tabId: string = this.viewModel.getActiveTabId();
    const urls: Array<string> | undefined = this.tabHistory.get(tabId);
    const index: number = this.tabHistoryIndex.get(tabId) ?? 0;
    if (urls === undefined || index + 1 >= urls.length) {
      return;
    }
    this.loadHistoryEntry(tabId, index + 1);
    this.syncTabs();
  }
"""
src = replace_method(src, 'back', back_body)
src = replace_method(src, 'forward', fwd_body)

# record history on navigate(): after loadUrlForSession success
old_load = """        if (engineIndex !== undefined) {
          GeckoViewBoot.loadUrlForSession(engineIndex, resolved);
        } else {
          GeckoViewBoot.loadUrl(resolved);
        }"""
assert src.count(old_load) == 1
new_load = """        if (engineIndex !== undefined) {
          GeckoViewBoot.loadUrlForSession(engineIndex, resolved);
        } else {
          GeckoViewBoot.loadUrl(resolved);
        }
        this.pushHistory(tabId, resolved);"""
src = src.replace(old_load, new_load)

# pageLoad stop: refresh from stacks (already calls refreshHistoryState)
io.open(p, 'w', encoding='utf-8').write(src)
print('OK ArkTS history implemented')
