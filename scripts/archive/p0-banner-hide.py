import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
a="""        this.recoveredCount = saved.tabs.length;
        this.showRecoveryBanner = true;"""
assert s.count(a)==1
s=s.replace(a,"""        this.recoveredCount = saved.tabs.length;
        this.showRecoveryBanner = true;
        setTimeout(() => {
          this.showRecoveryBanner = false;
        }, 8000);""")
io.open(p,'w',encoding='utf-8').write(s)
print('banner auto-hide added')
