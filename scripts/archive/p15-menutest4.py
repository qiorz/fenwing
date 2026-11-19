import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
old="""        this.menuSeq += 1;
        AppStorage.setOrCreate('geckoMenu', sample);
        AppStorage.setOrCreate('geckoMenuSeq', this.menuSeq);
        hilog.info(DOMAIN, 'GeckoBoot', 'menu test payload injected');"""
assert s.count(old)==1
new="""        setTimeout(() => {
          this.menuSeq += 1;
          AppStorage.setOrCreate('geckoMenu', sample);
          AppStorage.setOrCreate('geckoMenuSeq', this.menuSeq);
          hilog.info(DOMAIN, 'GeckoBoot', 'menu test payload injected');
        }, 2500);"""
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('menutest delayed')
