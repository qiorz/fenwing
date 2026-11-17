import io
p='/mnt/d/ff-ohos/work/firefoxport/entry/src/main/ets/entryability/EntryAbility.ets'
s=io.open(p,encoding='utf-8').read()
old="      GeckoViewBoot.init('https://example.com/', dir);"
assert s.count(old)==1
bench = (
 'const BENCH_HTML: string = \'<html><head><title>bench</title></head><body style="background:#fff">\'\n'
 '  + \'<script>function ms(f){const t=performance.now();f();return Math.round(performance.now()-t);}\'\n'
 '  + \'function run(){var a=ms(function(){var s=0;for(let i=0;i<20000000;i++){s+=i%7;}});\'\n'
 '  + \'var b=ms(function(){var x=0;for(let i=0;i<2000000;i++){x+=Math.sqrt(i)*1.0001;}});\'\n'
 '  + \'var c=ms(function(){var s="";for(let i=0;i<200000;i++){s+=String.fromCharCode(65+(i%26));}});\'\n'
 '  + \'var d=ms(function(){var o={a:1,b:[1,2,3],c:"x"};var j="";for(let i=0;i<100000;i++){j=JSON.stringify(o);}});\'\n'
 '  + \'var e=ms(function(){var arr=[];for(let i=0;i<300000;i++){arr.push(i);}arr.sort(function(p,q){return q-p;});});\'\n'
 '  + \'document.title="BENCH loop="+a+" math="+b+" str="+c+" json="+d+" sort="+e;}\'\n'
 '  + \'setTimeout(run,600);setTimeout(function(){document.title=document.title+" t="+Math.round(performance.now());},2000);\'\n'
 '  + \'</script></body></html>\';\n'
)
s = s.replace(old, "      GeckoViewBoot.init('data:text/html,' + encodeURIComponent(BENCH_HTML), dir);")
# insert BENCH_HTML before "export default class EntryAbility"
anchor="export default class EntryAbility extends UIAbility {"
assert s.count(anchor)==1
s = s.replace(anchor, bench + anchor)
io.open(p,'w',encoding='utf-8').write(s)
print('bench page wired')
