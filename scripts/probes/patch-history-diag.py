#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add diagnostics + extra refresh triggers for the history state."""
import io

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
src = io.open(p, encoding='utf-8').read()

old = """  private refreshHistoryState(): void {
    try {
      const history = GeckoViewBoot.sessionHistory();
      this.canGoBack = history.index > 0;
      this.canGoForward = history.index + 1 < history.count;
    } catch (error) {
      this.canGoBack = false;
      this.canGoForward = false;
    }
  }"""
new = """  private refreshHistoryState(): void {
    try {
      const history = GeckoViewBoot.sessionHistory();
      this.canGoBack = history.index > 0;
      this.canGoForward = history.index + 1 < history.count;
      hilog.info(DOMAIN, TAG, 'history index=%{public}d count=%{public}d back=%{public}s fwd=%{public}s',
        history.index, history.count, `${this.canGoBack}`, `${this.canGoForward}`);
    } catch (error) {
      this.canGoBack = false;
      this.canGoForward = false;
      hilog.warn(DOMAIN, TAG, 'sessionHistory failed: %{public}s', JSON.stringify(error));
    }
  }"""
assert src.count(old) == 1
src = src.replace(old, new)

# also refresh shortly after URL change (history updates asynchronously)
old2 = """    this.currentUrl = this.geckoUrl;
    hilog.info(DOMAIN, TAG, 'engine url -> %{public}s (session=%{public}s)', this.geckoUrl, this.geckoSession);"""
assert src.count(old2) == 1
new2 = old2 + """
    setTimeout(() => {
      this.refreshHistoryState();
    }, 600);"""
src = src.replace(old2, new2)

io.open(p, 'w', encoding='utf-8').write(src)
print('OK history diagnostics added')
