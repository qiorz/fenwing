import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="""  private openDownload(id: string): void {
    let path: string = '';"""
assert s.count(old)==1
s=s.replace(old,"""  private openDownload(id: string): void {
    if (this.contextRef === undefined) {
      return;
    }
    let path: string = '';""")
io.open(p,'w',encoding='utf-8').write(s)
print('context guard added')
