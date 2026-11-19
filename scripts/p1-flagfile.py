import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
if 'hwdecode.off' not in s:
    s=s.replace("    AppStorage.setOrCreate('softDecode', this.paramIsOne(want, 'swdecode'));",
'''    AppStorage.setOrCreate('softDecode', this.paramIsOne(want, 'swdecode'));
    try {
      const flag = `${this.context.filesDir}/hwdecode.off`;
      if (this.paramIsOne(want, 'swdecode')) {
        const f = fileIo.openSync(flag, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY);
        fileIo.closeSync(f);
      } else {
        fileIo.unlinkSync(flag);
      }
    } catch (e) {
      hilog.warn(DOMAIN, 'GeckoBoot', 'hwdecode flag failed: %{public}s', JSON.stringify(e));
    }''')
io.open(p,'w',encoding='utf-8').write(s)
print('flag file wired:', 'hwdecode.off' in s)
