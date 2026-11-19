import io,re
R='/mnt/d/ff-ohos/work/firefoxport'
p=R+'/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
html=('<html><head><title>b</title></head><body><script>'
 'function ms(f){var t=performance.now();f();return Math.round(performance.now()-t);}'
 'function fib(n){return n<2?n:fib(n-1)+fib(n-2);}'
 'function run(){var r=[];for(var k=0;k<3;k++){var a=ms(function(){fib(27);});'
 'var b=ms(function(){var o={x:0};for(var i=0;i<5000000;i++){o.x+=i;}});'
 'var c=ms(function(){var a=[];for(var i=0;i<1000000;i++){a.push(i);}a.map(function(v){return v*2;}).reduce(function(p,q){return p+q;},0);});'
 'var d=ms(function(){var s="";for(var i=0;i<50000;i++){s+="ab";}s.split("").join("");});'
 'r.push("fib="+a+",obj="+b+",arr="+c+",str="+d);}document.title="BENCH "+r.join(" | ");}'
 'setTimeout(run,800);</script></body></html>')
lit=html.replace('\\','\\\\').replace("'","\\'")
s=re.sub(r"const BENCH[^\n]*=.*?(?=\nexport default class)","",s,flags=re.S)
s=s.replace('export default class EntryAbility extends UIAbility {',"const BENCH_PAGE_HTML: string = '"+lit+"';\n\nexport default class EntryAbility extends UIAbility {",1)
old="      GeckoViewBoot.init('https://example.com/', dir);"
assert s.count(old)==1
s=s.replace(old,"""      const bp = this.context.filesDir + '/bench.html';
      try {
        const fd = fs.openSync(bp, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
        fs.writeSync(fd.fd, BENCH_PAGE_HTML);
        fs.closeSync(fd);
      } catch (e) {}
      GeckoViewBoot.init('file://' + bp, dir);""")
io.open(p,'w',encoding='utf-8').write(s)
print('bench ready')
