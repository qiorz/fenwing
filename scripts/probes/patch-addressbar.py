import io

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/components/AddressBar.ets'
s = io.open(p, encoding='utf-8').read()

old = """      this.navButton('←', this.canGoBack, () => {
        this.onBack();
      })
      this.navButton('→', this.canGoForward, () => {
        this.onForward();
      })"""
assert s.count(old) == 1, s.count(old)
new = """      Button('←')
        .fontSize(16)
        .fontColor(this.canGoBack ? '#E6E6F0' : '#4A4A5C')
        .backgroundColor('#1C1C26')
        .borderRadius(8)
        .width(36)
        .height(36)
        .enabled(this.canGoBack)
        .onClick(() => {
          this.onBack();
        })
      Button('→')
        .fontSize(16)
        .fontColor(this.canGoForward ? '#E6E6F0' : '#4A4A5C')
        .backgroundColor('#1C1C26')
        .borderRadius(8)
        .width(36)
        .height(36)
        .enabled(this.canGoForward)
        .onClick(() => {
          this.onForward();
        })"""
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('AddressBar back/forward inlined')
