import io
R='/mnt/d/ff-ohos/work/firefoxport'
# BrowserPage: four modes + legacy migration
p=R+'/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="""    let ua: string = '';
    if (this.uaMode === 'windows') {
      ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0';
    } else if (this.uaMode === 'mobile') {
      ua = 'Mozilla/5.0 (Android 13; Mobile; rv:142.0) Gecko/142.0 Firefox/142.0';
    } else {
      ua = 'Mozilla/5.0 (HarmonyOS 5.0; Mobile; rv:142.0) Gecko/142.0 Firefox/142.0';
    }"""
assert s.count(old)==1
new="""    let mode: string = this.uaMode;
    if (mode === 'harmony') {
      mode = 'standard';
    } else if (mode === 'windows') {
      mode = 'desktop';
    }
    let ua: string = '';
    if (mode === 'chrome') {
      ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
    } else if (mode === 'desktop') {
      ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0';
    } else if (mode === 'mobile') {
      ua = 'Mozilla/5.0 (Android 13; Mobile; rv:142.0) Gecko/142.0 Firefox/142.0';
    } else {
      ua = 'Mozilla/5.0 (HarmonyOS 5.0; Mobile; rv:142.0) Gecko/142.0 Firefox/142.0';
    }"""
s=s.replace(old,new)
s=s.replace("  @State private uaMode: string = 'harmony';","  @State private uaMode: string = 'standard';")
io.open(p,'w',encoding='utf-8').write(s)

# SettingsView: four labelled buttons in two rows
p=R+'/entry/src/main/ets/views/SettingsView.ets'
s=io.open(p,encoding='utf-8').read()
old="""        Row({ space: 8 }) {
          this.uaButton('HarmonyOS', 'harmony')
          this.uaButton('移动版', 'mobile')
          this.uaButton('Windows', 'windows')
        }
        .width('100%')"""
assert s.count(old)==1
new="""        Row({ space: 8 }) {
          this.uaButton('标准（Gecko）', 'standard')
          this.uaButton('手机', 'mobile')
        }
        .width('100%')
        Row({ space: 8 }) {
          this.uaButton('桌面', 'desktop')
          this.uaButton('Chrome 兼容', 'chrome')
        }
        .width('100%')"""
s=s.replace(old,new)
s=s.replace("  @Prop uaMode: string = 'harmony';","  @Prop uaMode: string = 'standard';")
io.open(p,'w',encoding='utf-8').write(s)
print('UA modes renamed')
