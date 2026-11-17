#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Title events carry a sequence number so identical titles still notify UI."""
import io

# EntryAbility: publish a sequenced title event
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
src = io.open(p, encoding='utf-8').read()

if 'geckoTitleEvent' not in src:
    a = """        onTitle: (title: string, url: string, session: string) => {
          if (title.length > 0) {
            AppStorage.setOrCreate('geckoTitle', title);
          }
        }"""
    assert src.count(a) == 1
    src = src.replace(a, """        onTitle: (title: string, url: string, session: string) => {
          if (title.length > 0) {
            // Sequence makes every event distinct even for equal titles.
            this.titleSeq += 1;
            AppStorage.setOrCreate('geckoTitleEvent', JSON.stringify({
              seq: this.titleSeq,
              session: session,
              title: title,
              url: url
            }));
          }
        }""")
    # add field after class opening line
    a = "export default class EntryAbility extends UIAbility {"
    assert src.count(a) == 1
    src = src.replace(a, a + "\n  private titleSeq: number = 0;")
    io.open(p, 'w', encoding='utf-8').write(src)
print('EntryAbility seq ok')

# BrowserPage: consume sequenced events
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
src = io.open(p, encoding='utf-8').read()

if 'geckoTitleEvent' not in src:
    a = "  @StorageProp('geckoTitle') @Watch('onGeckoTitleChanged') geckoTitle: string = '';"
    assert src.count(a) == 1
    src = src.replace(a, "  @StorageProp('geckoTitleEvent') @Watch('onGeckoTitleChanged') geckoTitleEvent: string = '';")

    a = """  /** Real page title from the engine keeps the tab chip and header in sync. */
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
  }"""
    assert src.count(a) == 1, src.count(a)
    src = src.replace(a, """  /** Real page title from the engine keeps the tab chip and header in sync. */
  private onGeckoTitleChanged(): void {
    if (this.geckoTitleEvent.length === 0) {
      return;
    }
    try {
      const event: TitleEvent = JSON.parse(this.geckoTitleEvent) as TitleEvent;
      if (event.title.length === 0) {
        return;
      }
      this.currentTitle = event.title;
      // Resolve the tab that owns this engine session, falling back to active.
      let tabId: string = this.viewModel.getActiveTabId();
      const engineIndex: number = Number(event.session);
      if (!Number.isNaN(engineIndex)) {
        const mapped: string | undefined = this.tabByEngineIndex.get(engineIndex);
        if (mapped !== undefined) {
          tabId = mapped;
        }
      }
      if (tabId.length > 0) {
        this.viewModel.markLoaded(tabId, event.title);
        hilog.info(DOMAIN, TAG, 'title applied tab=%{public}s title=%{public}s seq=%{public}d',
          tabId, event.title, event.seq);
        this.syncTabs();
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'title event parse failed: %{public}s', JSON.stringify(error));
    }
  }""")

    # TitleEvent interface next to other local types (append at end of file)
    src = src.rstrip() + """

/** Sequenced page-title event published by EntryAbility. */
interface TitleEvent {
  seq: number;
  session: string;
  title: string;
  url: string;
}
"""
    io.open(p, 'w', encoding='utf-8').write(src)
print('BrowserPage seq ok')
