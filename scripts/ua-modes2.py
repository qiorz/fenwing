import io
R='/mnt/d/ff-ohos/work/firefoxport'
p=R+'/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="    this.uaMode = this.settings.getUserAgentMode();"
assert s.count(old)==1
s=s.replace(old,"""    this.uaMode = this.settings.getUserAgentMode();
    if (this.uaMode === 'harmony') {
      this.uaMode = 'standard';
      this.settings.setUserAgentMode('standard');
    } else if (this.uaMode === 'windows') {
      this.uaMode = 'desktop';
      this.settings.setUserAgentMode('desktop');
    }""")
io.open(p,'w',encoding='utf-8').write(s)
p=R+'/entry/src/main/ets/views/SettingsView.ets'
s=io.open(p,encoding='utf-8').read()
s=s.replace(".backgroundColor(this.uaMode === mode ? '#2A3550' : '#17171F')",
            ".backgroundColor(this.uaMode === mode ? '#3A5A9A' : '#17171F')")
s=s.replace(".fontColor(this.uaMode === mode ? '#CFE0FF' : '#A0A0B8')",
            ".fontColor(this.uaMode === mode ? '#FFFFFF' : '#A0A0B8')")
io.open(p,'w',encoding='utf-8').write(s)
print('ua selection style + migration')
