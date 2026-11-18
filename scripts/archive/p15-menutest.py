import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
a="      GeckoViewBoot.registerAll(handlers);"
assert s.count(a)==1
if 'menutest' not in s:
    s=s.replace(a, a+"""
      if (this.paramIsOne(want, 'menutest')) {
        const sample = JSON.stringify({
          menuId: 9001,
          title: '',
          anchor: { x: 260, y: 180, w: 0, h: 0 },
          items: [
            { kind: 'item', id: 1, label: '刷新页面', accel: 'Ctrl+R', disabled: false, checked: false, hidden: false, items: [] },
            { kind: 'item', id: 2, label: '复制链接', accel: 'Ctrl+C', disabled: false, checked: false, hidden: false, items: [] },
            { kind: 'separator', id: 0, label: '', accel: '', disabled: false, checked: false, hidden: false, items: [] },
            { kind: 'checkbox', id: 3, label: '显示工具栏', accel: '', disabled: false, checked: true, hidden: false, items: [] },
            { kind: 'item', id: 4, label: '禁用项示例', accel: '', disabled: true, checked: false, hidden: false, items: [] }
          ]
        });
        this.menuSeq += 1;
        AppStorage.setOrCreate('geckoMenu', sample);
        AppStorage.setOrCreate('geckoMenuSeq', this.menuSeq);
        hilog.info(DOMAIN, 'GeckoBoot', 'menu test payload injected');
      }""")
    io.open(p,'w',encoding='utf-8').write(s)
print('menutest injected')
