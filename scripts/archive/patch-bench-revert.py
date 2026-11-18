import io, re
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()

# remove bench const + bench write block, restore init URL
s = re.sub(r"const BENCH_PAGE_HTML[^\n]*=.*?(?=\nexport default class)", "", s, flags=re.S)
s = re.sub(
    r"      const benchPath = this\.context\.filesDir \+ '/bench\.html';\n"
    r"(?:.|\n)*?      GeckoViewBoot\.init\('file://' \+ benchPath, dir\);",
    "      GeckoViewBoot.init('https://example.com/', dir);", s)
assert "BENCH_PAGE_HTML" not in s, 'bench const left'
assert "file://' + benchPath" not in s, 'bench init left'
io.open(p, 'w', encoding='utf-8').write(s)
print('EntryAbility restored; init line:', [l.strip() for l in s.splitlines() if 'GeckoViewBoot.init' in l])
