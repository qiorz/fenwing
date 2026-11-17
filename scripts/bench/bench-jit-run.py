import io,re
ROOT='/mnt/d/ff-ohos/work/firefoxport'
p=ROOT+'/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
html=('<html><head><title>bench</title></head><body style="background:#fff"><script>'
 'function ms(f){const t=performance.now();f();return Math.round(performance.now()-t);}'
 'function run(){var a=ms(function(){var s=0;for(let i=0;i<20000000;i++){s+=i%7;}});'
 'var b=ms(function(){var x=0;for(let i=0;i<2000000;i++){x+=Math.sqrt(i)*1.0001;}});'
 'var c=ms(function(){var s="";for(let i=0;i<20000;i++){s+=String.fromCharCode(65+(i%26));}});'
 'var d=ms(function(){var o={a:1,b:[1,2,3],c:"x"};var j="";for(let i=0;i<50000;i++){j=JSON.stringify(o);}});'
 'var e=ms(function(){var arr=[];for(let i=0;i<100000;i++){arr.push(i);}arr.sort(function(p,q){return q-p;});});'
 'document.title="BENCH loop="+a+" math="+b+" str="+c+" json="+d+" sort="+e;}'
 'setTimeout(run,600);</script></body></html>')
lit=html.replace('\\','\\\\').replace("'","\\'")
s=re.sub(r"const BENCH[^\n]*=.*?(?=\nexport default class)","",s,flags=re.S)
s=s.replace('export default class EntryAbility extends UIAbility {',"const BENCH_PAGE_HTML: string = '"+lit+"';\n\nexport default class EntryAbility extends UIAbility {",1)
# write bench + init
import_line="import { GeckoViewBoot, GeckoViewHandlers } from 'gecko';"
assert s.count(import_line)==1
s=s.replace(import_line,import_line+"\nimport { GeckoEngine } from 'gecko';")
old="      GeckoViewBoot.init('https://example.com/', dir);"
assert s.count(old)==1
new=("      const benchPath = this.context.filesDir + '/bench.html';\n"
 "      try {\n        const fd = fs.openSync(benchPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);\n"
 "        fs.writeSync(fd.fd, BENCH_PAGE_HTML);\n        fs.closeSync(fd);\n      } catch (e) {}\n"
 "      GeckoViewBoot.init('file://' + benchPath, dir);\n"
 "      setTimeout(() => {\n"
 "        const tail = GeckoEngine.readLogTail(`${this.context.filesDir}/gecko_xre_diag.txt`, 20000);\n"
 "        for (let i = 0; i < tail.length; i += 1000) { hilog.info(DOMAIN, 'Diag', '%{public}s', tail.substring(i, i + 1000)); }\n"
 "      }, 12000);")
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('bench+dump wired')
