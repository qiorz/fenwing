#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Page-title sync (idempotent): geckoview.js pushes active tab title via
airweb-tab-state; ArkTS consumes via registerTabStateCallback."""
import io

# ---------------------------------------------------------------- geckoview.js
p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
src = io.open(p, encoding='utf-8').read()

if 'ohosNotifyActiveTitle' not in src:
    helper = """
// ohos: 把活跃标签的标题/URL 推给 ArkTS(airweb-tab-state 信封,裸 JSON 转发)
function ohosNotifyActiveTitle() {
  try {
    const browser = TabManager.getBrowserBySessionId(TabManager._selectedSessionId);
    if (!browser) {
      return;
    }
    let title = "";
    let url = "";
    try {
      title = browser.contentTitle || "";
    } catch (e) {}
    try {
      url = browser.currentURI ? browser.currentURI.spec : "";
    } catch (e) {}
    if (!title) {
      try {
        const doc = browser.contentDocument;
        if (doc && doc.title) {
          title = doc.title;
        }
      } catch (e) {}
    }
    Services.obs.notifyObservers(
      null,
      "airweb-tab-state",
      JSON.stringify({
        session: String(TabManager._selectedSessionId || ""),
        title: title,
        url: url,
      })
    );
  } catch (e) {
    dump(`[OHOS_TITLE] notify failed: ${e}\\n`);
  }
}

function startup() {"""
    assert src.count('\nfunction startup() {') == 1
    src = src.replace('\nfunction startup() {', helper, 1)

    anchor = "  InitializationTracker.onInitialized(performance.now());"
    assert src.count(anchor) == 1
    src = src.replace(anchor,
        "  // ohos: 标题同步(初始 + DOMTitleChanged)\n"
        "  window.addEventListener(\"DOMTitleChanged\", function () { ohosNotifyActiveTitle(); }, true);\n"
        "  setTimeout(ohosNotifyActiveTitle, 1200);\n"
        "  setTimeout(ohosNotifyActiveTitle, 3000);\n"
        "  InitializationTracker.onInitialized(performance.now());")

    anchor2 = "    window.tab = null;\n    debug`TabManager.switchSession → ${aSessionId}`;"
    assert src.count(anchor2) == 1
    src = src.replace(anchor2,
        "    window.tab = null;\n"
        "    setTimeout(ohosNotifyActiveTitle, 300);\n"
        "    debug`TabManager.switchSession → ${aSessionId}`;")

# createBrowserForSession notify (separate, may be missing)
anchor3 = "    return browser;\n  },\n\n  /**\n   * 切换活跃标签(秒切,不重载)。"
assert src.count(anchor3) == 1, src.count(anchor3)
if 'setTimeout(ohosNotifyActiveTitle, 900);' not in src:
    src = src.replace(anchor3,
        "    setTimeout(ohosNotifyActiveTitle, 900);\n"
        "    return browser;\n  },\n\n  /**\n   * 切换活跃标签(秒切,不重载)。")

io.open(p, 'w', encoding='utf-8').write(src)
print('geckoview.js ok; marker count:', src.count('ohosNotifyActiveTitle'))

# ---------------------------------------------------------------- d.ts
p = '/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/cpp/types/libgeckoview/index.d.ts'
src = io.open(p, encoding='utf-8').read()
if 'registerTabStateCallback' not in src:
    a = "export const registerProgressCallback: (callback: (progress: number) => void) => void;"
    assert src.count(a) == 1
    src = src.replace(a, a + "\nexport const registerTabStateCallback: (callback: (json: string) => void) => void;")
    io.open(p, 'w', encoding='utf-8').write(src)
print('d.ts ok')

# ---------------------------------------------------------------- GeckoViewBoot
p = '/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
src = io.open(p, encoding='utf-8').read()
if 'onTitle' not in src:
    a = "  onIme?: (state: string) => void;"
    assert src.count(a) == 1
    src = src.replace(a, a + "\n  onTitle?: (title: string, url: string, session: string) => void;")

    a = "      if (handlers.onIme !== undefined) {"
    assert src.count(a) == 1
    block = """      geckoview.registerTabStateCallback((json: string) => {
        try {
          const payload: TabTitlePayload = JSON.parse(json) as TabTitlePayload;
          const title: string = payload.title !== undefined ? payload.title : '';
          const url: string = payload.url !== undefined ? payload.url : '';
          const session: string = payload.session !== undefined ? payload.session : '';
          if (title.length === 0 && url.length === 0) {
            return;
          }
          hilog.info(DOMAIN, TAG, 'title session=%{public}s title=%{public}s', session, title);
          if (handlers.onTitle !== undefined) {
            handlers.onTitle(title, url, session);
          }
        } catch (error) {
          hilog.warn(DOMAIN, TAG, 'tab-state parse failed: %{public}s', JSON.stringify(error));
        }
      });
""" + a
    src = src.replace(a, block, 1)

    a = """/** Plain mirror of the native surface-size payload. */"""
    assert src.count(a) == 1
    src = src.replace(a, """/** Envelope pushed by geckoview.js for active-tab title/url sync. */
export interface TabTitlePayload {
  session?: string;
  title?: string;
  url?: string;
}

/** Plain mirror of the native surface-size payload. */""")
    io.open(p, 'w', encoding='utf-8').write(src)
print('GeckoViewBoot ok')

# ---------------------------------------------------------------- EntryAbility
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
src = io.open(p, encoding='utf-8').read()
if "geckoTitle" not in src:
    a = """        onIme: (state: string) => {
          AppStorage.setOrCreate('geckoImeState', state);
        }"""
    assert src.count(a) == 1
    src = src.replace(a, a + """,
        onTitle: (title: string, url: string, session: string) => {
          if (title.length > 0) {
            AppStorage.setOrCreate('geckoTitle', title);
          }
        }""")
    io.open(p, 'w', encoding='utf-8').write(src)
print('EntryAbility ok')

# ---------------------------------------------------------------- BrowserPage
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
src = io.open(p, encoding='utf-8').read()
if 'onGeckoTitleChanged' not in src:
    a = "  @StorageProp('geckoPageLoad') @Watch('onGeckoPageLoadChanged') geckoPageLoad: string = '';"
    assert src.count(a) == 1
    src = src.replace(a, a + "\n  @StorageProp('geckoTitle') @Watch('onGeckoTitleChanged') geckoTitle: string = '';")

    a = "  private onGeckoPageLoadChanged(): void {"
    assert src.count(a) == 1
    src = src.replace(a, """  /** Real page title from the engine keeps the tab chip and header in sync. */
  private onGeckoTitleChanged(): void {
    if (this.geckoTitle.length === 0) {
      return;
    }
    this.currentTitle = this.geckoTitle;
    const activeTabId: string = this.viewModel.getActiveTabId();
    if (activeTabId.length > 0) {
      this.viewModel.markLoaded(activeTabId, this.geckoTitle);
      this.syncTabs();
    }
  }

  private onGeckoPageLoadChanged(): void {""")

if '<title>新标签页</title>' not in src:
    old_start = "const START_PAGE_HTML: string = 'data:text/html,' + encodeURIComponent(\n  '<html><body style="
    assert src.count(old_start) == 1
    src = src.replace(old_start, "const START_PAGE_HTML: string = 'data:text/html,' + encodeURIComponent(\n  '<html><head><title>新标签页</title></head><body style=")

io.open(p, 'w', encoding='utf-8').write(src)
print('BrowserPage ok')
