import io
R='/mnt/d/ff-ohos/work/firefoxport'
p=R+'/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="    AppStorage.setOrCreate('engineUnclean', unclean);"
assert s.count(a)==1
if "skipResume" not in s:
    s=s.replace(a,a+"\n    AppStorage.setOrCreate('skipResume', this.paramIsOne(want, 'noresume'));")
    io.open(p,'w',encoding='utf-8').write(s)
p=R+'/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
if 'skipResume' not in s:
    a="  @StorageProp('engineUnclean') engineUnclean: boolean = false;"
    assert s.count(a)==1
    s=s.replace(a,a+"\n  @StorageProp('skipResume') skipResume: boolean = false;")
    a="    const saved: SavedSession | undefined = this.store.load();\n    if (saved !== undefined && saved.tabs.length > 0) {"
    assert s.count(a)==1
    s=s.replace(a,"    const saved: SavedSession | undefined = this.skipResume ? undefined : this.store.load();\n    if (saved !== undefined && saved.tabs.length > 0) {")
    io.open(p,'w',encoding='utf-8').write(s)
print('skipResume wired')
