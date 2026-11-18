#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P2-2: engine-driven history, address-bar suggestions, demo image."""
import io

R = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- AddressBar
p = R + '/entry/src/main/ets/components/AddressBar.ets'
s = io.open(p, encoding='utf-8').read()
if 'onInput' not in s:
    a = "  onStop: () => void = () => {\n  };"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  onInput: (text: string) => void = () => {\n  };")
    a = """        .onChange((value: string) => {
          this.draft = value;
        })"""
    assert s.count(a) == 1
    s = s.replace(a, """        .onChange((value: string) => {
          this.draft = value;
          this.onInput(value);
        })""")
    a = """        .onSubmit(() => {
          this.onNavigate(this.draft);
        })"""
    assert s.count(a) == 1
    s = s.replace(a, """        .onSubmit(() => {
          this.onInput('');
          this.onNavigate(this.draft);
        })""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('AddressBar onInput ok')

# ---------------------------------------------------------------- BrowserPage
p = R + '/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f'{old[:60]!r} count={s.count(old)}'
    s = s.replace(old, new, n)

rep("  @State private contentWidth: number = 0;",
    """  @State private contentWidth: number = 0;
  @State private suggestions: Array<string> = [];
  @State private showSuggestions: boolean = false;
  private lastHistoryUrl: string = '';""")

# engine-driven history on load stop
rep("""    } else {
      this.stopLoadWatchdog();
      this.refreshHistoryState();
    }""",
    """    } else {
      this.stopLoadWatchdog();
      this.refreshHistoryState();
      this.recordEngineHistory();
    }""")

# helpers before onGeckoPageLoadChanged
rep("  private onGeckoPageLoadChanged(): void {",
    """  /** Records the active engine URL into history once per navigation. */
  private recordEngineHistory(): void {
    if (this.privateMode) {
      return;
    }
    const url: string = this.currentUrl;
    if (!url.startsWith('http') || url === this.lastHistoryUrl) {
      return;
    }
    this.lastHistoryUrl = url;
    try {
      const entry = HistoryEntry.create(PROFILE_ID, url, this.currentTitle);
      this.database.addHistory(entry).then(() => {
        this.refreshPanels();
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'engine history write failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'engine history create failed');
    }
  }

  private onAddressInput(text: string): void {
    if (text.length === 0) {
      this.showSuggestions = false;
      return;
    }
    const query: string = text.toLowerCase();
    const seen: Array<string> = new Array<string>();
    const hits: Array<string> = new Array<string>();
    const add = (value: string): void => {
      if (value.length === 0 || value === text || seen.indexOf(value) >= 0) {
        return;
      }
      const lower: string = value.toLowerCase();
      if (lower.indexOf(query) < 0 && lower.indexOf('http') !== 0) {
        return;
      }
      if (lower.indexOf(query) < 0) {
        return;
      }
      seen.push(value);
      hits.push(value);
    };
    for (let i = 0; i < this.bookmarks.length && hits.length < 8; i++) {
      add(this.bookmarks[i].url);
    }
    for (let i = 0; i < this.historyEntries.length && hits.length < 8; i++) {
      add(this.historyEntries[i].url);
    }
    this.suggestions = hits;
    this.showSuggestions = hits.length > 0;
  }

  private pickSuggestion(url: string): void {
    this.showSuggestions = false;
    this.navigate(url);
  }

  private onGeckoPageLoadChanged(): void {""")

# navigate(): dedupe history
rep("""        const entry = HistoryEntry.create(PROFILE_ID, resolved, title);
        await this.database.addHistory(entry);""",
    """        const entry = HistoryEntry.create(PROFILE_ID, resolved, title);
        await this.database.addHistory(entry);
        this.lastHistoryUrl = resolved;""")

# AddressBar props
rep("""        onNavigate: (input: string) => {
          this.navigate(input);
        },""",
    """        onNavigate: (input: string) => {
          this.showSuggestions = false;
          this.navigate(input);
        },
        onInput: (text: string) => {
          this.onAddressInput(text);
        },""")

# suggestions UI right after AddressBar block
marker = "      if (this.downloadVisible) {"
assert s.count(marker) == 1
s = s.replace(marker, """      if (this.showSuggestions && this.suggestions.length > 0) {
        Column({ space: 2 }) {
          ForEach(this.suggestions, (value: string) => {
            Text(value)
              .fontSize(12)
              .fontColor('#CFE0FF')
              .width('100%')
              .padding({ left: 12, right: 12, top: 7, bottom: 7 })
              .backgroundColor('#17171F')
              .maxLines(1)
              .textOverflow({ overflow: TextOverflow.Ellipsis })
              .onClick(() => {
                this.pickSuggestion(value);
              })
          }, (value: string) => value)
        }
        .width('100%')
        .backgroundColor('#12121A')
      }

""" + marker)

io.open(p, 'w', encoding='utf-8').write(s)
print('BrowserPage history + suggestions ok')

# ---------------------------------------------------------------- demo image
p = R + '/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()
if 'id="img"' not in s:
    a = '<p><a href="https://example.com/">示例链接</a></p>'
    assert s.count(a) == 1
    png = 'iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAWklEQVR4nO3BMQEAAADCoPVPbQ0PoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4NcAAT8AAX8VZ7YAAAAASUVORK5CYII='
    s = s.replace(a, a + '<p><img id="img" src="data:image/png;base64,' + png + '" width="240" height="240"></p>')
    io.open(p, 'w', encoding='utf-8').write(s)
print('demo image added')
