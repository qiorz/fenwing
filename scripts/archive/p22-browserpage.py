import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()

def rep(old,new,n=1):
    global s
    assert s.count(old)==n, f'{old[:50]!r} count={s.count(old)}'
    s=s.replace(old,new,n)

# import fileUri
rep("import { picker, fileIo as p1fs } from '@kit.CoreFileKit';",
    "import { picker, fileIo as p1fs, fileUri } from '@kit.CoreFileKit';")

# title handler: open-tab envelope
rep("""      const event: TitleEvent = JSON.parse(this.geckoTitleEvent) as TitleEvent;
      if (event.title.length === 0) {
        return;
      }""",
    """      const event: TitleEvent = JSON.parse(this.geckoTitleEvent) as TitleEvent;
      if (event.session === '__opentab__') {
        this.openUrlInNewTab(event.url);
        return;
      }
      if (event.title.length === 0) {
        return;
      }""")

# new tab helper before onGeckoPageLoadChanged
rep("  private onGeckoPageLoadChanged(): void {",
    """  /** Creates a tab + engine session for a URL requested by the chrome menu. */
  private openUrlInNewTab(url: string): void {
    if (url.length === 0) {
      return;
    }
    const created = this.viewModel.createTab(url);
    const engineIndex: number = this.nextEngineIndex++;
    this.bindEngineSession(created.id, engineIndex);
    this.viewModel.activateTab(created.id);
    GeckoViewBoot.createSession(engineIndex, url);
    GeckoViewBoot.switchToSession(engineIndex);
    this.viewModel.navigate(created.id, url);
    this.pushHistory(created.id, url);
    this.startLoadWatchdog();
    this.repaintSoon();
    this.syncTabs();
    hilog.info(DOMAIN, TAG, 'openUrlInNewTab %{public}s idx=%{public}d', url, engineIndex);
  }

  private onGeckoPageLoadChanged(): void {""")

# download handlers before retryDownload or cancelDownload
rep("  private async cancelDownload(id: string): Promise<void> {",
    """  private openDownload(id: string): void {
    const record: DownloadRecord | undefined = this.downloadRecords.find((r: DownloadRecord) => r.id === id);
    if (record === undefined || record.localPath.length === 0) {
      return;
    }
    try {
      const uri: string = fileUri.getUriFromPath(record.localPath);
      this.contextRef.startAbility({
        action: 'ohos.want.action.viewData',
        uri: uri,
        type: 'text/plain'
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'open download failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'open download error');
    }
  }

  private clearDownloads(): void {
    const records: Array<DownloadRecord> = this.downloadRecords;
    for (let i = 0; i < records.length; i++) {
      const path: string = records[i].localPath;
      if (path.length > 0) {
        try {
          p1fs.unlinkSync(path);
        } catch (error) {
        }
      }
    }
    this.database.clearDownloads(PROFILE_ID).then(() => {
      this.refreshPanels();
    }).catch((error: Object) => {
      hilog.warn(DOMAIN, TAG, 'clear downloads failed');
    });
  }

  private cancelDownload(id: string): void {""")

# DownloadsView props
rep("""            onRetry: (id: string) => {
              this.retryDownload(id);
            },""",
    """            onRetry: (id: string) => {
              this.retryDownload(id);
            },
            onOpen: (id: string) => {
              this.openDownload(id);
            },
            onClear: () => {
              this.clearDownloads();
            },""")

io.open(p,'w',encoding='utf-8').write(s)
print('BrowserPage P2-2 patched')
