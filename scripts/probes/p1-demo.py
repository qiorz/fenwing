#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add a --ps demo page with <input type=file> and a download link for P1 tests."""
import io

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()

if 'DEMO_PAGE_HTML' not in s:
    html = ('<html><head><title>P1 demo</title></head><body style="font-size:28px;padding:40px">'
            '<a href="https://example.com/">link</a>'
            '<p><input type="file" id="f" style="font-size:28px;width:600px"></p>'
            '<p><a href="data:text/plain,hello-download" download="hello.txt" '
            'style="display:inline-block;padding:20px;background:#4C6FFF;color:#fff">下载文件</a></p>'
            '</body></html>')
    literal = html.replace('\\', '\\\\').replace("'", "\\'")
    const = "const DEMO_PAGE_HTML: string = '" + literal + "';\n\n"
    anchor = 'export default class EntryAbility extends UIAbility {'
    assert s.count(anchor) == 1
    s = s.replace(anchor, const + anchor, 1)

    old = "      if (overrideUrl.length > 0) {"
    assert s.count(old) == 1
    s = s.replace(old, """      if (this.paramIsOne(want, 'demo')) {
        const demoPath: string = this.context.filesDir + '/demo.html';
        try {
          const demoFd = fs.openSync(demoPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
          fs.writeSync(demoFd.fd, DEMO_PAGE_HTML);
          fs.closeSync(demoFd);
        } catch (demoError) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'demo write failed');
        }
        startUrl = 'file://' + demoPath;
      }
      if (overrideUrl.length > 0) {""")
    io.open(p, 'w', encoding='utf-8').write(s)
print('demo page wired')
