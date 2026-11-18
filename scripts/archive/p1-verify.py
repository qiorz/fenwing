#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1 verification helpers: richer demo page + download/picker diagnostics."""
import io, re

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- demo page
p = ROOT + '/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()

html = ('<html><head><title>P1 demo</title></head><body style="font-size:26px;padding:36px">'
        '<p><input type="file" id="f" style="font-size:26px;width:620px"></p>'
        '<p><button onclick="dl()" style="font-size:26px;padding:16px">下载测试</button></p>'
        '<p><button onclick="fs()" style="font-size:26px;padding:16px">全屏测试</button></p>'
        '<script>'
        'function dl(){var b=new Blob(["hello-download"],{type:"text/plain"});'
        'var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="hello.txt";'
        'document.body.appendChild(a);a.click();}'
        'function fs(){document.documentElement.requestFullscreen();}'
        '</script></body></html>')
literal = html.replace('\\', '\\\\').replace("'", "\\'")

s2 = re.sub(r"const DEMO_PAGE_HTML[^\n]*=.*?(?=\nexport default class)", "", s, flags=re.S)
anchor = 'export default class EntryAbility extends UIAbility {'
assert s2.count(anchor) == 1
s2 = s2.replace(anchor, "const DEMO_PAGE_HTML: string = '" + literal + "';\n\n" + anchor, 1)
io.open(p, 'w', encoding='utf-8').write(s2)
print('demo page updated')

# ---------------------------------------------------------------- diagnostics
p = ROOT + '/entry/src/main/ets/pages/BrowserPage.ets'
s = io.open(p, encoding='utf-8').read()

a = "      this.downloadText = text;"
assert s.count(a) == 1
s = s.replace(a, """      hilog.info(DOMAIN, TAG, 'download event: %{public}s', text);
      this.downloadText = text;""")

b = """    try {
      const wrapper: PickerEvent = JSON.parse(this.geckoFilePicker) as PickerEvent;"""
assert s.count(b) == 1
s = s.replace(b, """    try {
      hilog.info(DOMAIN, TAG, 'file picker request: %{public}s', this.geckoFilePicker);
      const wrapper: PickerEvent = JSON.parse(this.geckoFilePicker) as PickerEvent;""")

c = "      const documentPicker = new picker.DocumentViewPicker(this.contextRef);"
assert s.count(c) == 1
s = s.replace(c, """      hilog.info(DOMAIN, TAG, 'opening system picker mode=%{public}s', req.mode);
      const documentPicker = new picker.DocumentViewPicker(this.contextRef);""")

d = "      const uris: Array<string> = await documentPicker.select(options);"
assert s.count(d) == 1
s = s.replace(d, """      const uris: Array<string> = await documentPicker.select(options);
      hilog.info(DOMAIN, TAG, 'picker returned %{public}d uris', uris === undefined ? 0 : uris.length);""")

io.open(p, 'w', encoding='utf-8').write(s)
print('diagnostics added')
