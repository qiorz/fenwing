import io
p='/mnt/d/ff-ohos/work/firefoxport/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
if 'static setCharPref' not in s:
    a="  static scroll(dx: number, dy: number, x: number, y: number): void {"
    assert s.count(a)==1
    s=s.replace(a, """  static setCharPref(name: string, value: string): void {
    hilog.info(DOMAIN, TAG, 'setCharPref %{public}s=%{public}s', name, value);
    geckoview.setCharPref(name, value);
  }

""" + a)
s=s.replace("geckoview.scroll(dx, dy, x, y, 0);","geckoview.scroll(dx, dy, x, y);")
io.open(p,'w',encoding='utf-8').write(s)
# AxisEvent undefined
p2='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/components/GeckoSurface.ets'
s2=io.open(p2,encoding='utf-8').read()
s2=s2.replace("const dx: number = event.axisHorizontal;","const dx: number = event.axisHorizontal ?? 0;")
s2=s2.replace("const dy: number = event.axisVertical;","const dy: number = event.axisVertical ?? 0;")
io.open(p2,'w',encoding='utf-8').write(s2)
print('prefs+axis fixed')
