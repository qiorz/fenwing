#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1 BrowserPage: download banner, file picker, fullscreen, zoom, find bar."""
import io

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f'anchor {old[:60]!r} count={s.count(old)}'
    s = s.replace(old, new, n)

# imports
if "from '@kit.CoreFileKit'" not in s:
    rep("import { common } from '@kit.AbilityKit';",
        "import { common } from '@kit.AbilityKit';\nimport { picker, fileIo as p1fs } from '@kit.CoreFileKit';\nimport { window as p1window } from '@kit.ArkUI';")

# fields
rep("  @State private canGoForward: boolean = false;",
    """  @State private canGoForward: boolean = false;
  @StorageProp('geckoDownload') @Watch('onDownloadEvent') geckoDownload: string = '';
  @StorageProp('geckoFilePicker') @Watch('onFilePickerEvent') geckoFilePicker: string = '';
  @StorageProp('geckoFullscreen') @Watch('onFullscreenChanged') geckoFullscreen: boolean = false;
  @State private downloadText: string = '';
  @State private downloadVisible: boolean = false;
  @State private zoomLevel: number = 1.0;
  @State private findVisible: boolean = false;
  @State private findQuery: string = '';
  @State private findMatchCase: boolean = false;
  private downloadHideTimer: number = -1;""")

# behaviour methods before bootstrap
anchor = "  private async bootstrap(): Promise<void> {"
assert s.count(anchor) == 1
methods = """  // -------------------- P1: downloads / picker / fullscreen / find / zoom ----
  private onDownloadEvent(): void {
    if (this.geckoDownload.length === 0) {
      return;
    }
    try {
      const event: DownloadEvent = JSON.parse(this.geckoDownload) as DownloadEvent;
      let text: string = '';
      if (event.type === 'start') {
        text = `开始下载：${event.filename !== undefined ? event.filename : event.url}`;
      } else if (event.type === 'progress') {
        const total: number = event.totalBytes !== undefined ? event.totalBytes : 0;
        const got: number = event.receivedBytes !== undefined ? event.receivedBytes : 0;
        const pct: number = total > 0 ? Math.round(got * 100 / total) : 0;
        text = `下载中：${pct}%`;
      } else if (event.type === 'complete') {
        text = `下载完成：${event.path}`;
        this.recordDownload(event, DownloadState.COMPLETED);
      } else if (event.type === 'failed') {
        text = `下载失败：${event.errorCode}`;
        this.recordDownload(event, DownloadState.FAILED);
      } else {
        return;
      }
      this.downloadText = text;
      this.downloadVisible = true;
      if (this.downloadHideTimer >= 0) {
        clearTimeout(this.downloadHideTimer);
      }
      if (event.type === 'complete' || event.type === 'failed') {
        this.downloadHideTimer = setTimeout(() => {
          this.downloadVisible = false;
        }, 5000);
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'download event parse failed: %{public}s', JSON.stringify(error));
    }
  }

  private recordDownload(event: DownloadEvent, state: DownloadState): void {
    try {
      const record = new DownloadRecord();
      record.id = `dl_${event.id}_${Date.now()}`;
      record.profileId = PROFILE_ID;
      record.url = event.url !== undefined ? event.url : '';
      record.fileName = event.filename !== undefined ? event.filename : '';
      record.totalBytes = event.totalBytes !== undefined ? event.totalBytes : 0;
      record.receivedBytes = event.receivedBytes !== undefined ? event.receivedBytes : record.totalBytes;
      record.state = state;
      record.localPath = event.path !== undefined ? event.path : '';
      record.createdAt = Date.now();
      this.database.upsertDownload(record).then(() => {
        this.refreshPanels();
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'download record failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'recordDownload failed: %{public}s', JSON.stringify(error));
    }
  }

  private onFilePickerEvent(): void {
    if (this.geckoFilePicker.length === 0) {
      return;
    }
    try {
      const wrapper: PickerEvent = JSON.parse(this.geckoFilePicker) as PickerEvent;
      const req: PickerRequest = JSON.parse(wrapper.req) as PickerRequest;
      this.openFilePicker(wrapper.id, req);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'file picker parse failed: %{public}s', JSON.stringify(error));
    }
  }

  private async openFilePicker(callbackId: number, req: PickerRequest): Promise<void> {
    try {
      const documentPicker = new picker.DocumentViewPicker(this.contextRef);
      const options = new picker.DocumentSelectOptions();
      options.maxSelectNumber = req.mode === 'multiple' ? 10 : 1;
      if (req.suffixes !== undefined && req.suffixes.length > 0) {
        options.fileSuffixFilters = req.suffixes;
      }
      const uris: Array<string> = await documentPicker.select(options);
      if (uris === undefined || uris.length === 0) {
        GeckoViewBoot.resolveFilePicker(callbackId, 1, '');
        return;
      }
      const paths: Array<string> = new Array<string>();
      for (let i = 0; i < uris.length; i++) {
        paths.push(uris[i].startsWith('file://') ? uris[i].substring(7) : uris[i]);
      }
      if (req.mode === 'multiple') {
        GeckoViewBoot.resolveFilePicker(callbackId, 0, JSON.stringify(paths));
      } else {
        GeckoViewBoot.resolveFilePicker(callbackId, 0, paths[0]);
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'openFilePicker failed/cancelled: %{public}s', JSON.stringify(error));
      GeckoViewBoot.resolveFilePicker(callbackId, 1, '');
    }
  }

  private onFullscreenChanged(): void {
    try {
      p1window.getLastWindow(this.contextRef).then((win: p1window.Window) => {
        win.setWindowLayoutFullScreen(this.geckoFullscreen);
        win.setWindowSystemBarEnable(this.geckoFullscreen ? [] : ['status', 'navigation']);
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'fullscreen apply failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'fullscreen failed: %{public}s', JSON.stringify(error));
    }
  }

  private zoomBy(delta: number): void {
    this.zoomLevel = Math.min(3.0, Math.max(0.5, this.zoomLevel + delta));
    GeckoViewBoot.setFullZoom(this.zoomLevel);
  }

  private findNext(backward: boolean): void {
    if (this.findQuery.length === 0) {
      return;
    }
    GeckoViewBoot.findInPage(this.findQuery, backward, this.findMatchCase);
  }

  private async bootstrap(): Promise<void> {"""
s = s.replace(anchor, methods)

# download banner UI after AddressBar
rep("""      })

      Stack({ alignContent: Alignment.Center }) {""",
    """      })

      if (this.downloadVisible) {
        Row({ space: 8 }) {
          Text(this.downloadText)
            .fontSize(12)
            .fontColor('#CFE3FF')
            .layoutWeight(1)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
          Text('收起')
            .fontSize(12)
            .fontColor('#8FA8CC')
            .onClick(() => {
              this.downloadVisible = false;
            })
        }
        .width('100%')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#182338')
      }

      Stack({ alignContent: Alignment.Center }) {""")

# find bar + zoom toolbar after content stack
rep("""      }
      .width('100%')
      .layoutWeight(1)

      if (this.statusMessage.length > 0) {""",
    """      }
      .width('100%')
      .layoutWeight(1)

      if (this.findVisible) {
        Row({ space: 8 }) {
          TextInput({ text: this.findQuery, placeholder: '页内查找' })
            .fontSize(13)
            .height(34)
            .layoutWeight(1)
            .backgroundColor('#1C1C26')
            .fontColor('#E6E6F0')
            .onChange((value: string) => {
              this.findQuery = value;
            })
            .onSubmit(() => {
              this.findNext(false);
            })
          Button('上一个')
            .fontSize(12)
            .height(34)
            .backgroundColor('#2A2A3A')
            .fontColor('#E6E6F0')
            .onClick(() => {
              this.findNext(true);
            })
          Button('下一个')
            .fontSize(12)
            .height(34)
            .backgroundColor('#2A2A3A')
            .fontColor('#E6E6F0')
            .onClick(() => {
              this.findNext(false);
            })
          Button('关闭')
            .fontSize(12)
            .height(34)
            .backgroundColor('#1C1C26')
            .fontColor('#8A8AA3')
            .onClick(() => {
              this.findVisible = false;
            })
        }
        .width('100%')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#12121A')
      }

      Row({ space: 8 }) {
        Button(this.findVisible ? '隐藏查找' : '查找')
          .fontSize(12)
          .height(30)
          .backgroundColor('#1C1C26')
          .fontColor('#C8C8DC')
          .onClick(() => {
            this.findVisible = !this.findVisible;
          })
        Blank()
        Button('−')
          .fontSize(16)
          .width(34)
          .height(30)
          .backgroundColor('#1C1C26')
          .fontColor('#E6E6F0')
          .onClick(() => {
            this.zoomBy(-0.1);
          })
        Text(`${Math.round(this.zoomLevel * 100)}%`)
          .fontSize(12)
          .fontColor('#A0A0B8')
          .width(48)
          .textAlign(TextAlign.Center)
        Button('+')
          .fontSize(16)
          .width(34)
          .height(30)
          .backgroundColor('#1C1C26')
          .fontColor('#E6E6F0')
          .onClick(() => {
            this.zoomBy(0.1);
          })
      }
      .width('100%')
      .padding({ left: 12, right: 12, top: 4, bottom: 4 })
      .backgroundColor('#0E0E12')

      if (this.statusMessage.length > 0) {""")

# local interfaces appended at end of file
s = s.rstrip() + """

interface DownloadEvent {
  type: string;
  id: number;
  url?: string;
  filename?: string;
  totalBytes?: number;
  receivedBytes?: number;
  path?: string;
  errorCode?: string;
}

interface PickerRequest {
  id: number;
  mode: string;
  title?: string;
  mimeTypes?: Array<string>;
  suffixes?: Array<string>;
}

interface PickerEvent {
  id: number;
  req: string;
}
"""

io.open(p, 'w', encoding='utf-8').write(s)
print('BrowserPage P1 patched, len', len(s))
