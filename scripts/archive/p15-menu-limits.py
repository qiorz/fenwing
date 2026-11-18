#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finish P1.5 menu limits: edge-aware placement, context-aware items,
copy actions, collapsible submenus."""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- geckoview.js
p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s = io.open(p, encoding='utf-8').read()

start = s.find('function ohosOpenContextMenu(aBrowser, aX, aY) {')
assert start > 0
end = s.find('\nfunction startup() {', start)
assert end > start
new_js = '''function ohosClipboardWrite(aText) {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(aText);
      return true;
    }
  } catch (e) {}
  try {
    const helper = Cc["@mozilla.org/widget/clipboardhelper;1"]
      .getService(Ci.nsIClipboardHelper);
    helper.copyString(aText);
    return true;
  } catch (e) {}
  return false;
}

function ohosBuildContextItems(aBrowser, aEvent) {
  const items = [];
  let doc = null;
  let win = null;
  try {
    doc = aBrowser.contentDocument;
    win = aBrowser.contentWindow;
  } catch (e) {}

  let target = null;
  try {
    target = doc.elementFromPoint(aEvent.clientX, aEvent.clientY);
  } catch (e) {}

  if (target && target.closest) {
    const link = target.closest("a[href]");
    if (link) {
      items.push({
        label: "复制链接地址",
        accel: "",
        run: () => ohosClipboardWrite(link.href),
      });
    }
    const img = target.closest("img");
    if (img && img.src) {
      items.push({
        label: "复制图片地址",
        accel: "",
        run: () => ohosClipboardWrite(img.src),
      });
    }
  }

  let selection = "";
  try {
    selection = win ? String(win.getSelection()) : "";
  } catch (e) {}
  if (selection.length > 0) {
    items.push({
      label: "复制选中文本",
      accel: "Ctrl+C",
      run: () => ohosClipboardWrite(selection),
    });
  }

  items.push({ label: "刷新页面", accel: "Ctrl+R", run: () => { try { aBrowser.reload(); } catch (e) {} } });
  items.push({ label: "后退", accel: "Alt+Left", run: () => { try { aBrowser.browsingContext.goBack(); } catch (e) {} } });
  items.push({ label: "前进", accel: "Alt+Right", run: () => { try { aBrowser.browsingContext.goForward(); } catch (e) {} } });

  items.push({
    label: "更多",
    accel: "",
    children: [
      {
        label: "复制页面地址",
        accel: "",
        run: () => {
          try {
            ohosClipboardWrite(aBrowser.currentURI.spec);
          } catch (e) {}
        },
      },
      {
        label: "复制页面标题",
        accel: "",
        run: () => ohosClipboardWrite(aBrowser.contentTitle || ""),
      },
    ],
  });

  return items;
}

function ohosFillMenu(aParent, aItems) {
  aItems.forEach((it) => {
    if (it.children && it.children.length > 0) {
      const menu = document.createXULElement("menu");
      menu.setAttribute("label", it.label);
      const sub = document.createXULElement("menupopup");
      ohosFillMenu(sub, it.children);
      menu.appendChild(sub);
      aParent.appendChild(menu);
    } else {
      const mi = document.createXULElement("menuitem");
      mi.setAttribute("label", it.label);
      if (it.accel) {
        mi.setAttribute("acceltext", it.accel);
      }
      mi.addEventListener("command", () => {
        try {
          if (it.run) {
            it.run();
          }
        } catch (e) {}
      });
      aParent.appendChild(mi);
    }
  });
}

function ohosOpenContextMenu(aBrowser, aX, aY, aEvent) {
  try {
    let popup = document.getElementById("ohos-content-context-menu");
    if (!popup) {
      popup = document.createXULElement("menupopup");
      popup.id = "contentAreaContextMenu";
      popup.setAttribute("type", "content");
      document.documentElement.appendChild(popup);
    }
    while (popup.firstChild) {
      popup.removeChild(popup.firstChild);
    }
    ohosFillMenu(popup, ohosBuildContextItems(aBrowser, aEvent));
    popup.openPopupAtScreen(aX, aY, true);
    dump(`[OHOS_CTX] open at ${aX},${aY}\\n`);
  } catch (e) {
    dump(`[OHOS_CTX] failed: ${e}\\n`);
  }
}
'''
s = s[:start] + new_js + s[end:]

# listener: pass event through
s = s.replace("ohosOpenContextMenu(browser, ev.screenX, ev.screenY);",
              "ohosOpenContextMenu(browser, ev.screenX, ev.screenY, ev);")
# autotest call: fabricate event-like object
s = s.replace("ohosOpenContextMenu(b, 420, 300);",
              "ohosOpenContextMenu(b, 420, 300, { clientX: 40, clientY: 40 });")
io.open(p, 'w', encoding='utf-8').write(s)
print('geckoview.js context items upgraded')

# ---------------------------------------------------------------- BrowserPage
p = ROOT + '/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f'anchor {old[:60]!r} count={s.count(old)}'
    s = s.replace(old, new, n)

# fields
rep("  @State private menuY: number = 0;",
    """  @State private menuY: number = 0;
  @State private contentWidth: number = 0;
  @State private contentHeight: number = 0;
  private menuTree: Array<MenuItem> = new Array<MenuItem>();
  private expandedMenuIds: Array<number> = new Array<number>();""")

# onMenuEvent: replace flatten/position block
old = """      const rows: Array<MenuRow> = new Array<MenuRow>();
      this.flattenMenu(payload.items, 0, rows);
      if (rows.length === 0) {
        return;
      }
      this.menuRows = rows;
      this.menuId = payload.menuId;
      const ax: number = payload.anchor !== undefined ? payload.anchor.x : 0;
      const ay: number = payload.anchor !== undefined ? payload.anchor.y : 0;
      const ah: number = payload.anchor !== undefined ? payload.anchor.h : 0;
      // Port delivers anchor in device px (CSS px * 3 in this chrome doc);
      // ArkUI positions are vp, and CSS px ~= vp here, so divide by 3.
      this.menuX = Math.max(8, Math.floor(ax / 3));
      this.menuY = Math.max(8, Math.floor((ay + ah) / 3));
      this.menuVisible = true;"""
assert s.count(old) == 1, s.count(old)
new = """      this.menuTree = payload.items;
      this.expandedMenuIds = new Array<number>();
      this.rebuildMenuRows();
      if (this.menuRows.length === 0) {
        return;
      }
      this.menuId = payload.menuId;
      const ax: number = payload.anchor !== undefined ? payload.anchor.x : 0;
      const ay: number = payload.anchor !== undefined ? payload.anchor.y : 0;
      const ah: number = payload.anchor !== undefined ? payload.anchor.h : 0;
      // Port delivers anchor in device px (CSS px * 3 in this chrome doc);
      // ArkUI positions are vp, and CSS px ~= vp here, so divide by 3.
      let x: number = Math.max(8, Math.floor(ax / 3));
      let y: number = Math.max(8, Math.floor((ay + ah) / 3));
      const menuWidth: number = 260;
      const menuHeight: number = Math.min(420, this.menuRows.length * 36 + 12);
      if (this.contentWidth > 0 && x + menuWidth > this.contentWidth - 8) {
        x = Math.max(8, this.contentWidth - menuWidth - 8);
      }
      if (this.contentHeight > 0 && y + menuHeight > this.contentHeight - 8) {
        y = Math.max(8, y - menuHeight - 8);
      }
      this.menuX = x;
      this.menuY = y;
      this.menuVisible = true;"""
s = s.replace(old, new)

# flattenMenu: add hasChildren/expanded + gating
old = """  private flattenMenu(items: Array<MenuItem>, depth: number, out: Array<MenuRow>): void {
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
  }"""
assert s.count(old) == 1, s.count(old)
new = """  private flattenMenu(items: Array<MenuItem>, depth: number, out: Array<MenuRow>): void {
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
      row.hasChildren = item.items !== undefined && item.items.length > 0;
      row.expanded = this.expandedMenuIds.indexOf(item.id) >= 0;
      out.push(row);
      if (row.hasChildren && row.expanded && depth < 3) {
        this.flattenMenu(item.items as Array<MenuItem>, depth + 1, out);
      }
    }
  }

  private rebuildMenuRows(): void {
    const rows: Array<MenuRow> = new Array<MenuRow>();
    this.flattenMenu(this.menuTree, 0, rows);
    this.menuRows = rows;
  }

  /** Expands/collapses a submenu row (port renders submenus flat). */
  private toggleMenuRow(row: MenuRow): void {
    const index: number = this.expandedMenuIds.indexOf(row.id);
    if (index >= 0) {
      this.expandedMenuIds.splice(index, 1);
    } else {
      this.expandedMenuIds.push(row.id);
    }
    this.rebuildMenuRows();
  }"""
s = s.replace(old, new)

# tapMenuRow: submenu toggles
old = """  private tapMenuRow(row: MenuRow): void {
    if (row.disabled || row.kind === 'separator' || row.id === 0) {
      return;
    }"""
assert s.count(old) == 1
new = """  private tapMenuRow(row: MenuRow): void {
    if (row.disabled || row.kind === 'separator' || row.id === 0) {
      return;
    }
    if (row.hasChildren) {
      this.toggleMenuRow(row);
      return;
    }"""
s = s.replace(old, new)

# UI: indicator glyph + area change on content stack
rep("Text(row.checked ? '✓' : '')", "Text(row.hasChildren ? (row.expanded ? '▾' : '▸') : (row.checked ? '✓' : ''))")

anchor = "      Stack({ alignContent: Alignment.Center }) {\n        GeckoSurface({"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor)
# add onAreaChange before the stack's layoutWeight(1)
start2 = s.index(anchor)
closeIdx = s.index("\n      .layoutWeight(1)", start2)
s = s[:closeIdx] + "\n      .onAreaChange((oldArea: Area, newArea: Area) => {\n        this.contentWidth = Number(newArea.width);\n        this.contentHeight = Number(newArea.height);\n      })" + s[closeIdx:]

# MenuRow fields
rep("""class MenuRow {
  kind: string = 'item';""", """class MenuRow {
  kind: string = 'item';
  hasChildren: boolean = false;
  expanded: boolean = false;""")

io.open(p, 'w', encoding='utf-8').write(s)
print('BrowserPage menu upgraded')
