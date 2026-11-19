import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
start=s.find('  private openDownload(id: string): void {')
end=s.find('  private clearDownloads(): void {', start)
assert start>0 and end>start
new='''  private openDownload(id: string): void {
    let path: string = '';
    for (let i = 0; i < this.downloadRecords.length; i++) {
      if (this.downloadRecords[i].id === id) {
        path = this.downloadRecords[i].localPath;
        break;
      }
    }
    if (path.length === 0) {
      return;
    }
    try {
      const uri: string = fileUri.getUriFromPath(path);
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

'''
s=s[:start]+new+s[end:]
io.open(p,'w',encoding='utf-8').write(s)
print('openDownload simplified')
