import io, re
p = '/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()

# strip any previous bench const block (const BENCH... up to the line before export default)
s = re.sub(r"const BENCH[^\n]*=.*?(?=\nexport default class)", "", s, flags=re.S)

html = (
 '<html><head><title>bench</title></head><body style="background:#fff">'
 '<script>function ms(f){const t=performance.now();f();return Math.round(performance.now()-t);}'
 'function run(){var a=ms(function(){var s=0;for(let i=0;i<2000000;i++){s+=i%7;}});'
 'var b=ms(function(){var x=0;for(let i=0;i<200000;i++){x+=Math.sqrt(i)*1.0001;}});'
 'var c=ms(function(){var s="";for(let i=0;i<10000;i++){s+=String.fromCharCode(65+(i%26));}});'
 'var d=ms(function(){var o={a:1,b:[1,2,3],c:"x"};var j="";for(let i=0;i<10000;i++){j=JSON.stringify(o);}});'
 'var e=ms(function(){var arr=[];for(let i=0;i<20000;i++){arr.push(i);}arr.sort(function(p,q){return q-p;});});'
 'document.title="BENCH loop="+a+" math="+b+" str="+c+" json="+d+" sort="+e;}'
 'setTimeout(run,600);</script></body></html>'
)
literal = html.replace('\\', '\\\\').replace("'", "\\'")
const_line = "const BENCH_PAGE_HTML: string = '" + literal + "';\n\n"

anchor = 'export default class EntryAbility extends UIAbility {'
assert s.count(anchor) == 1, s.count(anchor)
s = s.replace(anchor, const_line + anchor)

old = "      GeckoViewBoot.init('data:text/html,' + encodeURIComponent(BENCH_HTML), dir);"
assert s.count(old) == 1, s.count(old)
new = ("      const benchPath = this.context.filesDir + '/bench.html';\n"
       "      try {\n"
       "        const benchFd = fs.openSync(benchPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);\n"
       "        fs.writeSync(benchFd.fd, BENCH_PAGE_HTML);\n"
       "        fs.closeSync(benchFd);\n"
       "        hilog.info(DOMAIN, 'GeckoBoot', 'bench page written: %{public}s', benchPath);\n"
       "      } catch (benchError) {\n"
       "        hilog.warn(DOMAIN, 'GeckoBoot', 'bench write failed: %{public}s', JSON.stringify(benchError));\n"
       "      }\n"
       "      GeckoViewBoot.init('file://' + benchPath, dir);")
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('bench file mode ok; len', len(s))
