import io, base64, re

svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><rect width="240" height="240" fill="#4C6FFF"/><circle cx="120" cy="120" r="60" fill="#FFD166"/><text x="120" y="130" font-size="28" text-anchor="middle" fill="#12121A">IMG</text></svg>'
svg64 = base64.b64encode(svg).decode()

html = (
    '<html><head><title>P1 demo</title></head><body style="font-size:26px;padding:36px">'
    '<p><a href="https://example.com/">示例链接</a></p>'
    '<p><a href="https://example.com/?blank=1" target="_blank">新标签链接</a></p>'
    '<p><img id="img" src="data:image/svg+xml;base64,' + svg64 + '" width="240" height="240"></p>'
    '<p><video id="v" src="__VIDEO__" autoplay loop muted playsinline controls width="640" height="360"></video></p>'
    '<p><input type="file" id="f" style="font-size:26px;width:620px"></p>'
    '<p><select id="s" style="font-size:26px;padding:10px"><option>AAA</option><option>BBB</option><option>CCC</option></select></p>'
    '<p><button onclick="dl()" style="font-size:26px;padding:16px">下载测试</button></p>'
    '<p><button onclick="fs()" style="font-size:26px;padding:16px">全屏测试</button></p>'
    '<script>'
    'function dl(){var b=new Blob(["hello-download"],{type:"text/plain"});'
    'var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="hello.txt";'
    'document.body.appendChild(a);a.click();}'
    'function fs(){document.documentElement.requestFullscreen();}'
    '</script></body></html>'
)

p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()
start = s.find('const DEMO_PAGE_HTML')
assert start > 0
end = s.find(';\n\nexport default class', start)
assert end > start
literal = html.replace('\\', '\\\\').replace("'", "\\'")
new = "const DEMO_PAGE_HTML: string = '" + literal + "'"
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('demo html rebuilt, has video:', '<video id="v"' in s)
