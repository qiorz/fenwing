import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()

# field
a="  @State private findMatchCase: boolean = false;"
assert s.count(a)==1
if 'fullscreenUi' not in s:
    s=s.replace(a,a+"\n  @State private fullscreenUi: boolean = false;")

# onFullscreenChanged: toggle shell
b="  private onFullscreenChanged(): void {"
assert s.count(b)==1
s=s.replace(b, b+"\n    this.fullscreenUi = this.geckoFullscreen;")

# wrap AddressBar block
start=s.index('      AddressBar({')
end=s.index('\n      })', start)+len('\n      })')
s=s[:start]+'      if (!this.fullscreenUi) {\n'+s[start:end]+'\n      }\n'+s[end:]

# wrap TabBar block
start=s.index('      TabBar({')
end=s.index('\n      })', start)+len('\n      })')
s=s[:start]+'      if (!this.fullscreenUi) {\n'+s[start:end]+'\n      }\n'+s[end:]

# exit-fullscreen overlay inside content stack: insert before loadError block
c="        if (this.loadError.length > 0) {"
assert s.count(c)==1
overlay="""        if (this.fullscreenUi) {
          Button('退出全屏')
            .fontSize(12)
            .height(30)
            .backgroundColor('#AA1C1C26')
            .fontColor('#E6E6F0')
            .margin({ top: 10 })
            .onClick(() => {
              this.fullscreenUi = false;
              GeckoViewBoot.exitFullscreen();
            })
        }
""" + c
s=s.replace(c, overlay)
io.open(p,'w',encoding='utf-8').write(s)
print('fullscreen ui added')
