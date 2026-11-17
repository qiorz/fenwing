#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finish M4 polish:
   1) GeckoViewBoot: per-session nav + session history
   2) libgeckoview d.ts declarations
   3) BrowserPage: back/forward/reload/stop wired to the active engine session
   4) EntryAbility: clear startupCache only when omni.ja content stamp changes
"""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- GeckoViewBoot
p = ROOT + '/gecko/src/main/ets/GeckoViewBoot.ets'
src = io.open(p, encoding='utf-8').read()
anchor = """  /** Forces the widget to repaint (used after tab switches). */
  static forceRepaint(): void {
    geckoview.forceRepaint();
  }"""
assert src.count(anchor) == 1, src.count(anchor)
addition = """  /** Forces the widget to repaint (used after tab switches). */
  static forceRepaint(): void {
    geckoview.forceRepaint();
  }

  static goBackForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'goBack session=%{public}d', sessionId);
    geckoview.goBackForSession(sessionId);
  }

  static goForwardForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'goForward session=%{public}d', sessionId);
    geckoview.goForwardForSession(sessionId);
  }

  static reloadForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'reloadSession session=%{public}d', sessionId);
    geckoview.reloadForSession(sessionId);
  }

  static stopForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'stopSession session=%{public}d', sessionId);
    geckoview.stopForSession(sessionId);
  }

  /** Session history of the active engine browser; throws when unavailable. */
  static sessionHistory(): SessionHistoryReport {
    const report = new SessionHistoryReport();
    const raw: SessionHistoryReport = geckoview.getSessionHistory() as SessionHistoryReport;
    report.index = raw.index;
    report.count = raw.count;
    return report;
  }"""
src = src.replace(anchor, addition)
# add report class next to SurfaceSizeReport
anchor2 = """/** Plain mirror of the native surface-size payload. */
export class SurfaceSizeReport {
  width: number = 0;
  height: number = 0;
}"""
assert src.count(anchor2) == 1
src = src.replace(anchor2, anchor2 + """

/** Session history position/count of the active engine browser. */
export class SessionHistoryReport {
  index: number = 0;
  count: number = 0;
}""")
io.open(p, 'w', encoding='utf-8').write(src)

# -------------------------------------------------------------------- d.ts
p = ROOT + '/gecko/src/main/cpp/types/libgeckoview/index.d.ts'
src = io.open(p, encoding='utf-8').read()
anchor = "export const forceRepaint: () => void;"
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + """

// Per-session navigation / history.
export const goBackForSession: (sessionId: number) => void;
export const goForwardForSession: (sessionId: number) => void;
export const reloadForSession: (sessionId: number) => void;
export const stopForSession: (sessionId: number) => void;
export const getSessionHistory: () => { index: number; count: number };""")
io.open(p, 'w', encoding='utf-8').write(src)

# -------------------------------------------------------------------- BrowserPage
p = ROOT + '/entry/src/main/ets/pages/BrowserPage.ets'
src = io.open(p, encoding='utf-8').read()

# states
anchor = "  @StorageProp('geckoPageLoad') @Watch('onGeckoPageLoadChanged') geckoPageLoad: string = '';"
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + """
  @State private canGoBack: boolean = false;
  @State private canGoForward: boolean = false;""")

# history refresh helper + page-load hook
anchor = """  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
  }"""
assert src.count(anchor) == 1
src = src.replace(anchor, """  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
    if (this.geckoPageLoad === 'stop') {
      this.refreshHistoryState();
    }
  }

  /** Mirrors the active engine session's history position into the UI. */
  private refreshHistoryState(): void {
    try {
      const history = GeckoViewBoot.sessionHistory();
      this.canGoBack = history.index > 0;
      this.canGoForward = history.index + 1 < history.count;
    } catch (error) {
      this.canGoBack = false;
      this.canGoForward = false;
    }
  }

  private back(): void {
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex === undefined) {
      return;
    }
    try {
      GeckoViewBoot.goBackForSession(engineIndex);
      this.repaintSoon();
      setTimeout(() => {
        this.refreshHistoryState();
      }, 400);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'goBack failed: %{public}s', JSON.stringify(error));
    }
  }

  private forward(): void {
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex === undefined) {
      return;
    }
    try {
      GeckoViewBoot.goForwardForSession(engineIndex);
      this.repaintSoon();
      setTimeout(() => {
        this.refreshHistoryState();
      }, 400);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'goForward failed: %{public}s', JSON.stringify(error));
    }
  }

  private reload(): void {
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex === undefined) {
      return;
    }
    try {
      GeckoViewBoot.reloadForSession(engineIndex);
      this.repaintSoon();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'reload failed: %{public}s', JSON.stringify(error));
    }
  }

  private stopLoading(): void {
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex !== undefined) {
      try {
        GeckoViewBoot.stopForSession(engineIndex);
      } catch (error) {
        hilog.warn(DOMAIN, TAG, 'stop failed: %{public}s', JSON.stringify(error));
      }
    }
    this.viewModel.markStopped(this.activeTabId);
  }""")

# AddressBar wiring
start = src.index('      AddressBar({')
end = src.index('\n      })', start) + len('\n      })')
new_block = """      AddressBar({
        url: this.currentUrl,
        canGoBack: this.canGoBack,
        canGoForward: this.canGoForward,
        loading: this.loading,
        privateMode: this.privateMode,
        onNavigate: (input: string) => {
          this.navigate(input);
        },
        onBack: () => {
          this.back();
        },
        onForward: () => {
          this.forward();
        },
        onReload: () => {
          this.reload();
        },
        onStop: () => {
          this.stopLoading();
        }
      })"""
src = src[:start] + new_block + src[end:]
io.open(p, 'w', encoding='utf-8').write(src)

# ---------------------------------------------------------------- EntryAbility
p = ROOT + '/entry/src/main/ets/entryability/EntryAbility.ets'
src = io.open(p, encoding='utf-8').read()
old = "      this.clearStartupCache(`${this.context.filesDir}/profile`);\n      GeckoViewBoot.init('https://example.com/', dir);"
assert src.count(old) == 1, src.count(old)
new = """      // Only clear the Gecko chrome-script cache when omni.ja content changed,
      // so cold starts stay fast after the first run of a given build.
      const stamp: string = this.omniStamp(bytes);
      const stampFile = dir + '/omni.stamp';
      let previousStamp: string = '';
      try {
        if (fs.accessSync(stampFile)) {
          previousStamp = fs.readTextSync(stampFile).trim();
        }
      } catch (error) {
        previousStamp = '';
      }
      if (previousStamp !== stamp) {
        this.clearStartupCache(`${this.context.filesDir}/profile`);
        try {
          const stampFd = fs.openSync(stampFile, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
          fs.writeSync(stampFd.fd, stamp);
          fs.closeSync(stampFd);
          hilog.info(DOMAIN, 'GeckoBoot', 'omni stamp updated: %{public}s', stamp);
        } catch (error) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'stamp write failed: %{public}s', JSON.stringify(error));
        }
      } else {
        hilog.info(DOMAIN, 'GeckoBoot', 'omni unchanged, startupCache kept');
      }
      GeckoViewBoot.init('https://example.com/', dir);"""
src = src.replace(old, new)

# add omniStamp helper before clearStartupCache
anchor = """  /**
   * Gecko caches compiled chrome scripts in <profile>/startupCache."""
assert src.count(anchor) == 1
helper = """  /** Cheap content stamp of omni.ja (length + sampled bytes) for cache gating. */
  private omniStamp(bytes: Uint8Array): string {
    let hash: number = 5381;
    const len: number = bytes.length;
    const head: number = Math.min(len, 16384);
    for (let i = 0; i < head; i++) {
      hash = (((hash * 33) | 0) + bytes[i]) | 0;
    }
    const tailStart: number = Math.max(0, len - 16384);
    for (let i = tailStart; i < len; i++) {
      hash = (((hash * 33) | 0) + bytes[i]) | 0;
    }
    return `${len}-${(hash >>> 0).toString(16)}`;
  }

""" + anchor
src = src.replace(anchor, helper)
io.open(p, 'w', encoding='utf-8').write(src)

print('OK: all polish patches applied')
