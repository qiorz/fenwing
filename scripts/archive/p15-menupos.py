import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/pages/BrowserPage.ets'
s=io.open(p,encoding='utf-8').read()
old="""      this.menuX = Math.max(8, ax);
      this.menuY = Math.max(8, ay + ah);"""
assert s.count(old)==1
new="""      // Port delivers anchor in device px (CSS px * 3 in this chrome doc);
      // ArkUI positions are vp, and CSS px ~= vp here, so divide by 3.
      this.menuX = Math.max(8, Math.floor(ax / 3));
      this.menuY = Math.max(8, Math.floor((ay + ah) / 3));"""
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('menu position scaled')
