import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/components/AddressBar.ets'
s=io.open(p,encoding='utf-8').read()
# back/forward: ASCII glyphs (arrow unicode may not render in button font)
s=s.replace("Button('←')","Button('<')").replace("Button('→')","Button('>')")
# replace the reload/stop navButton block with explicit labelled button
old="""      if (this.loading) {
        this.navButton('✕', true, () => {
          this.onStop();
        })
      } else {
        this.navButton('⟳', true, () => {
          this.onReload();
        })
      }"""
assert s.count(old)==1
new="""      Button(this.loading ? '停止' : '刷新')
        .fontSize(12)
        .fontColor('#E6E6F0')
        .backgroundColor('#1C1C26')
        .borderRadius(6)
        .width(48)
        .height(36)
        .padding(0)
        .onClick(() => {
          if (this.loading) {
            this.onStop();
          } else {
            this.onReload();
          }
        })"""
s=s.replace(old,new)
# bump back/forward font size for ASCII
s=s.replace("""        .fontSize(16)
        .fontColor(this.canGoBack ? '#E6E6F0' : '#4A4A5C')""","""        .fontSize(20)
        .fontColor(this.canGoBack ? '#E6E6F0' : '#4A4A5C')""")
s=s.replace("""        .fontSize(16)
        .fontColor(this.canGoForward ? '#E6E6F0' : '#4A4A5C')""","""        .fontSize(20)
        .fontColor(this.canGoForward ? '#E6E6F0' : '#4A4A5C')""")
io.open(p,'w',encoding='utf-8').write(s)
print('addressbar buttons updated')
