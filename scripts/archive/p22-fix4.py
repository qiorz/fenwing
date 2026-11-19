import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="""    for (let i = 0; i < this.downloadRecords.length; i++) {
      if (this.downloadRecords[i].id === id) {
        path = this.downloadRecords[i].localPath;
        break;
      }
    }"""
assert s.count(old)==1
s=s.replace(old,"""    for (const record of this.downloadRecords) {
      if (record.id === id) {
        path = record.localPath;
        break;
      }
    }""")
io.open(p,'w',encoding='utf-8').write(s)
print('for-of fix')
