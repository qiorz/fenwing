#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P2-2 shell: open link in new tab, save image, download management."""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'
R = ROOT

# ---------------------------------------------------------------- geckoview.js
p = '/home/dev/ff/gecko/obj-aarch64-unknown-linux-ohos/dist/bin/chrome/geckoview/content/geckoview.js'
s = io.open(p, encoding='utf-8').read()
old = """    const link = target.closest("a[href]");
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
    }"""
assert s.count(old) == 1, s.count(old)
new = """    const link = target.closest("a[href]");
    if (link) {
      items.push({
        label: "在新标签页打开链接",
        accel: "",
        run: () => {
          try {
            Services.obs.notifyObservers(null, "airweb-tab-state",
              JSON.stringify({ session: "__opentab__", title: "", url: link.href }));
          } catch (e) {}
        },
      });
      items.push({
        label: "复制链接地址",
        accel: "",
        run: () => ohosClipboardWrite(link.href),
      });
    }
    const img = target.closest("img");
    if (img && img.src) {
      items.push({
        label: "保存图片",
        accel: "",
        run: () => {
          try {
            const a = doc.createElement("a");
            a.href = img.src;
            a.download = (img.src.split("/").pop() || "image");
            doc.body.appendChild(a);
            a.click();
            a.remove();
          } catch (e) {}
        },
      });
      items.push({
        label: "复制图片地址",
        accel: "",
        run: () => ohosClipboardWrite(img.src),
      });
    }"""
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('geckoview.js menu items added')

# ---------------------------------------------------------------- BrowserDatabase
p = R + '/entry/src/main/ets/data/BrowserDatabase.ets'
s = io.open(p, encoding='utf-8').read()
if 'deleteDownload' not in s:
    anchor = """  async listDownloads(profileId: string): Promise<Array<DownloadRecord>> {"""
    assert s.count(anchor) == 1
    s = s.replace(anchor, """  async deleteDownload(id: string): Promise<void> {
    const predicates = new relationalStore.RdbPredicates('downloads');
    predicates.equalTo('id', id);
    await this.requireStore().delete(predicates);
  }

  async clearDownloads(profileId: string): Promise<void> {
    const predicates = new relationalStore.RdbPredicates('downloads');
    predicates.equalTo('profile_id', profileId);
    await this.requireStore().delete(predicates);
  }

""" + anchor)
    io.open(p, 'w', encoding='utf-8').write(s)
print('database download delete ok')

# ---------------------------------------------------------------- DownloadsView
p = R + '/entry/src/main/ets/views/DownloadsView.ets'
s = io.open(p, encoding='utf-8').read()
if 'onOpen' not in s:
    a = """  onRefresh: () => void = () => {
  };"""
    assert s.count(a) == 1
    s = s.replace(a, a + """
  onOpen: (id: string) => void = () => {
  };
  onClear: () => void = () => {
  };""")
    a = """        Button('刷新')
          .fontSize(12)
          .height(30)
          .backgroundColor('#1C1C26')
          .fontColor('#C9C9DE')
          .onClick(() => {
            this.onRefresh();
          })"""
    assert s.count(a) == 1
    s = s.replace(a, """        Button('清空')
          .fontSize(12)
          .height(30)
          .backgroundColor('#2A1A1F')
          .fontColor('#E6A3A3')
          .margin({ right: 6 })
          .onClick(() => {
            this.onClear();
          })
        Button('刷新')
          .fontSize(12)
          .height(30)
          .backgroundColor('#1C1C26')
          .fontColor('#C9C9DE')
          .onClick(() => {
            this.onRefresh();
          })""")
    a = """                  if (record.state === DownloadState.DOWNLOADING || record.state === DownloadState.QUEUED) {"""
    assert s.count(a) == 1
    s = s.replace(a, """                  if (record.state === DownloadState.COMPLETED && record.localPath.length > 0) {
                    Button('打开')
                      .fontSize(12)
                      .height(28)
                      .backgroundColor('#1F2A1F')
                      .fontColor('#A8E6B0')
                      .onClick(() => {
                        this.onOpen(record.id);
                      })
                  }
""" + a)
    io.open(p, 'w', encoding='utf-8').write(s)
print('DownloadsView actions ok')
