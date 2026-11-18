#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1.5: menu overlay + compact toolbar + TabBar menu wiring."""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- EntryAbility
p = ROOT + '/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()
if 'onMenu' not in s:
    a = "  private titleSeq: number = 0;"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  private menuSeq: number = 0;")

    a = "        onDownload: (json: string) => {"
    assert s.count(a) == 1
    s = s.replace(a, """        onMenu: (json: string) => {
          this.menuSeq += 1;
          AppStorage.setOrCreate('geckoMenu', json);
          AppStorage.setOrCreate('geckoMenuSeq', this.menuSeq);
        },
""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('EntryAbility menu handler ok')

# ---------------------------------------------------------------- BrowserPage
p = ROOT + '/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f'anchor {old[:70]!r} count={s.count(old)}'
    s = s.replace(old, new, n)

# fields
rep("  @State private fullscreenUi: boolean = false;",
    """  @State private fullscreenUi: boolean = false;
  @StorageProp('geckoMenuSeq') @Watch('onMenuEvent') geckoMenuSeq: number = 0;
  @StorageProp('geckoMenu') geckoMenuRaw: string = '';
  @State private menuVisible: boolean = false;
  @State private menuId: number = 0;
  @State private menuRows: Array<MenuRow> = [];
  @State private menuX: number = 0;
  @State private menuY: number = 0;""")

# menu methods before zoomBy
rep("  private zoomBy(delta: number): void {",
    """  private onMenuEvent(): void {
    if (this.geckoMenuRaw.length === 0) {
      return;
    }
    try {
      const payload: MenuPayload = JSON.parse(this.geckoMenuRaw) as MenuPayload;
      if (payload === undefined || payload.items === undefined || payload.items.length === 0) {
        return;
      }
      const rows: Array<MenuRow> = new Array<MenuRow>();
      this.flattenMenu(payload.items, 0, rows);
      if (rows.length === 0) {
        return;
      }
      this.menuRows = rows;
      this.menuId = payload.menuId;
      const ax: number = payload.anchor !== undefined ? payload.anchor.x : 0;
      const ay: number = payload.anchor !== undefined ? payload.anchor.y : 0;
      const ah: number = payload.anchor !== undefined ? payload.anchor.h : 0;
      this.menuX = Math.max(8, ax);
      this.menuY = Math.max(8, ay + ah);
      this.menuVisible = true;
      hilog.info(DOMAIN, TAG, 'menu shown id=%{public}d rows=%{public}d', this.menuId, rows.length);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'menu parse failed: %{public}s', JSON.stringify(error));
    }
  }

  private flattenMenu(items: Array<MenuItem>, depth: number, out: Array<MenuRow>): void {
    for (let i = 0; i < items.length; i++) {
      const item: MenuItem = items[i];
      if (item.hidden) {
        continue;
      }
      const row = new MenuRow();
      row.kind = item.kind;
      row.id = item.id;
      row.label = item.label;
      row.accel = item.accel;
      row.disabled = item.disabled;
      row.checked = item.checked;
      row.depth = depth;
      out.push(row);
      if (item.items !== undefined && item.items.length > 0 && depth < 2) {
        this.flattenMenu(item.items, depth + 1, out);
      }
    }
  }

  private tapMenuRow(row: MenuRow): void {
    if (row.disabled || row.kind === 'separator' || row.id === 0) {
      return;
    }
    GeckoViewBoot.resolveMenuCommand(this.menuId, row.id, 0);
    this.menuVisible = false;
  }

  private closeMenu(sendToGecko: boolean): void {
    if (sendToGecko) {
      GeckoViewBoot.closeNativeMenu(this.menuId);
    }
    this.menuVisible = false;
  }

  private zoomBy(delta: number): void {""")

# remove old zoom row
start = s.index("      Row({ space: 8 }) {\n        Button(this.findVisible ? '隐藏查找' : '查找')")
end = s.index("      .backgroundColor('#0E0E12')", start) + len("      .backgroundColor('#0E0E12')")
s = s[:start] + "" + s[end:]

# replace panel toolbar row with compact row incl. find/zoom
start = s.index("      Row({ space: 6 }) {\n        this.panelButton('书签', PANEL_BOOKMARKS)")
end = s.index("      .justifyContent(FlexAlign.Start)", start) + len("      .justifyContent(FlexAlign.Start)")
compact = """      if (!this.fullscreenUi) {
        Row({ space: 4 }) {
          this.panelButton('书签', PANEL_BOOKMARKS)
          this.panelButton('历史', PANEL_HISTORY)
          this.panelButton('下载', PANEL_DOWNLOADS)
          this.panelButton('设置', PANEL_SETTINGS)
          Button('收藏')
            .fontSize(11)
            .height(26)
            .backgroundColor('#1F2A1F')
            .fontColor('#A8E6B0')
            .borderRadius(6)
            .onClick(() => {
              this.addCurrentBookmark();
            })
          Button(this.privateMode ? '退出私密' : '私密')
            .fontSize(11)
            .height(26)
            .backgroundColor(this.privateMode ? '#2A1F3A' : '#17171F')
            .fontColor(this.privateMode ? '#C9A7FF' : '#A0A0B8')
            .borderRadius(6)
            .onClick(() => {
              this.togglePrivateMode();
            })
          Blank()
          Button(this.findVisible ? '隐藏查找' : '查找')
            .fontSize(11)
            .height(26)
            .backgroundColor('#1C1C26')
            .fontColor('#C8C8DC')
            .borderRadius(6)
            .onClick(() => {
              this.findVisible = !this.findVisible;
            })
          Button('−')
            .fontSize(14)
            .width(28)
            .height(26)
            .backgroundColor('#1C1C26')
            .fontColor('#E6E6F0')
            .borderRadius(6)
            .onClick(() => {
              this.zoomBy(-0.1);
            })
          Text(`${Math.round(this.zoomLevel * 100)}%`)
            .fontSize(10)
            .fontColor('#A0A0B8')
            .width(36)
            .textAlign(TextAlign.Center)
          Button('+')
            .fontSize(14)
            .width(28)
            .height(26)
            .backgroundColor('#1C1C26')
            .fontColor('#E6E6F0')
            .borderRadius(6)
            .onClick(() => {
              this.zoomBy(0.1);
            })
        }
        .width('100%')
        .padding({ left: 8, right: 8, top: 3, bottom: 3 })
        .backgroundColor('#0E0E12')
      }"""
s = s[:start] + compact + s[end:]

# compact panelButton
rep("""  panelButton(label: string, panel: string) {
    Button(label)
      .fontSize(12)
      .height(32)""", """  panelButton(label: string, panel: string) {
    Button(label)
      .fontSize(11)
      .height(26)""")
rep("""      .fontColor(this.activePanel === panel ? '#CFE0FF' : '#A0A0B8')
      .borderRadius(8)""", """      .fontColor(this.activePanel === panel ? '#CFE0FF' : '#A0A0B8')
      .borderRadius(6)""")

# TabBar menu wiring
rep("""        privateMode: this.privateMode,
        onSelectTab: (tabId: string) => {""", """        privateMode: this.privateMode,
        onMenu: () => {
          this.openPanel(PANEL_SETTINGS);
        },
        onSelectTab: (tabId: string) => {""")

# menu overlay inside content stack (before closing of Stack)
rep("""        if (this.loadError.length > 0) {""", """        if (this.menuVisible) {
          Stack() {
            Column() {
            }
            .width('100%')
            .height('100%')
            .onClick(() => {
              this.closeMenu(true);
            })
            Scroll() {
              Column({ space: 2 }) {
                ForEach(this.menuRows, (row: MenuRow) => {
                  if (row.kind === 'separator') {
                    Divider()
                      .strokeWidth(1)
                      .color('#2A2A3A')
                      .margin({ top: 3, bottom: 3 })
                  } else {
                    Row({ space: 6 }) {
                      Text(row.checked ? '✓' : '')
                        .fontSize(12)
                        .fontColor('#7FD18B')
                        .width(14)
                      Text(row.label)
                        .fontSize(13)
                        .fontColor(row.disabled ? '#5A5A6E' : '#E6E6F0')
                        .layoutWeight(1)
                        .maxLines(1)
                        .textOverflow({ overflow: TextOverflow.Ellipsis })
                      if (row.accel.length > 0) {
                        Text(row.accel)
                          .fontSize(10)
                          .fontColor('#6E6E85')
                      }
                    }
                    .width('100%')
                    .padding({ left: 10 + row.depth * 12, right: 10, top: 7, bottom: 7 })
                    .borderRadius(6)
                    .backgroundColor('#242433')
                    .onClick(() => {
                      this.tapMenuRow(row);
                    })
                  }
                }, (row: MenuRow) => `${row.id}|${row.label}|${row.checked}|${row.disabled}`)
              }
              .width('100%')
            }
            .width(260)
            .constraintSize({ maxHeight: 420 })
            .scrollBar(BarState.Off)
            .backgroundColor('#1C1C26')
            .borderRadius(10)
            .padding(6)
            .position({ x: Math.min(this.menuX, 900), y: Math.min(this.menuY, 700) })
          }
          .width('100%')
          .height('100%')
        }

        if (this.loadError.length > 0) {""")

# interfaces appended
s = s.rstrip() + """

interface MenuAnchor {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface MenuItem {
  kind: string;
  id: number;
  label: string;
  accel: string;
  icon?: string;
  disabled: boolean;
  checked: boolean;
  hidden: boolean;
  items?: Array<MenuItem>;
}

interface MenuPayload {
  menuId: number;
  title?: string;
  anchor?: MenuAnchor;
  point?: boolean;
  items: Array<MenuItem>;
}

class MenuRow {
  kind: string = 'item';
  id: number = 0;
  label: string = '';
  accel: string = '';
  disabled: boolean = false;
  checked: boolean = false;
  depth: number = 0;
}
"""

io.open(p, 'w', encoding='utf-8').write(s)
print('BrowserPage P1.5 patched, len', len(s))
