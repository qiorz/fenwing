import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace("  private cancelDownload(id: string): void {","  private async cancelDownload(id: string): Promise<void> {",1)
s=s.replace("""    if (record === undefined || record.localPath.length === 0) {
      return;
    }
    try {
      const uri: string = fileUri.getUriFromPath(record.localPath);""","""    if (record === undefined) {
      return;
    }
    if (record.localPath.length === 0) {
      return;
    }
    try {
      const uri: string = fileUri.getUriFromPath(record.localPath);""")
io.open(p,'w',encoding='utf-8').write(s)
print('fixed async + narrowing')
