#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runtime-selectable A/B benchmark + JIT/interpreter switch via want params.

aa start -a EntryAbility -b com.example.firefoxport --ps perf 1            # JIT
aa start ... --ps perf 1 --ps nojit 1                                     # interpreter
"""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ---------------------------------------------------------------- GeckoViewBoot
p = ROOT + '/gecko/src/main/ets/GeckoViewBoot.ets'
s = io.open(p, encoding='utf-8').read()

old = """  static init(url: string, resourceDir: string): void {
    hilog.info(DOMAIN, TAG, 'initFirefox url=%{public}s resourceDir=%{public}s', url, resourceDir);
    geckoview.initFirefox({
      url: url,
      resourceDir: resourceDir,
      // ACL granted: XPCOMInit's RWX probe enables the full JIT backend.
      commandlineArgs: '',
      uiMode: 'classic'
    });"""
if old not in s:
    # tolerate the slightly different comment text
    import re
    m = re.search(r"  static init\(url: string, resourceDir: string\): void \{\n(?:.|\n)*?\n  \}", s)
    assert m, 'init() block not found'
    old = m.group(0)
    s = s[:m.start()] + """  static init(url: string, resourceDir: string, commandlineArgs: string = ''): void {
    hilog.info(DOMAIN, TAG, 'initFirefox url=%{public}s resourceDir=%{public}s args=%{public}s',
      url, resourceDir, commandlineArgs);
    geckoview.initFirefox({
      url: url,
      resourceDir: resourceDir,
      commandlineArgs: commandlineArgs,
      uiMode: 'classic'
    });""" + s[m.start() + len(m.group(0)):]
else:
    s = s.replace(old, """  static init(url: string, resourceDir: string, commandlineArgs: string = ''): void {
    hilog.info(DOMAIN, TAG, 'initFirefox url=%{public}s resourceDir=%{public}s args=%{public}s',
      url, resourceDir, commandlineArgs);
    geckoview.initFirefox({
      url: url,
      resourceDir: resourceDir,
      commandlineArgs: commandlineArgs,
      uiMode: 'classic'
    });""")
io.open(p, 'w', encoding='utf-8').write(s)
print('GeckoViewBoot.init extended')

# ---------------------------------------------------------------- EntryAbility
p = ROOT + '/entry/src/main/ets/entryability/EntryAbility.ets'
s = io.open(p, encoding='utf-8').read()

bench_html = (
    '<html><head><title>bench</title></head><body><script>'
    'function ms(f){var t=performance.now();f();return Math.round(performance.now()-t);}'
    'function fib(n){return n<2?n:fib(n-1)+fib(n-2);}'
    'function run(){var r=[];for(var k=0;k<3;k++){'
    'var a=ms(function(){fib(27);});'
    'var b=ms(function(){var o={x:0};for(var i=0;i<5000000;i++){o.x+=i;}});'
    'var c=ms(function(){var a=[];for(var i=0;i<1000000;i++){a.push(i);}'
    'a.map(function(v){return v*2;}).reduce(function(p,q){return p+q;},0);});'
    'var d=ms(function(){var s="";for(var i=0;i<50000;i++){s+="ab";}s.split("").join("");});'
    'r.push("fib="+a+",obj="+b+",arr="+c+",str="+d);}'
    'document.title="BENCH "+r.join(" | ");}'
    'setTimeout(run,800);</script></body></html>')

literal = bench_html.replace('\\', '\\\\').replace("'", "\\'")
const = "const BENCH_PAGE_HTML: string = '" + literal + "';\n\n"
if 'const BENCH_PAGE_HTML' not in s:
    anchor = 'export default class EntryAbility extends UIAbility {'
    assert s.count(anchor) == 1
    s = s.replace(anchor, const + anchor, 1)

# onCreate passes params
s = s.replace("    this.bootGecko();", """    const perf: boolean = this.paramIsOne(want, 'perf');
    const nojit: boolean = this.paramIsOne(want, 'nojit');
    hilog.info(DOMAIN, 'GeckoBoot', 'launch params perf=%{public}s nojit=%{public}s',
      `${perf}`, `${nojit}`);
    this.bootGecko(perf, nojit);""", 1)

s = s.replace("  private bootGecko(): void {", "  private bootGecko(perf: boolean, nojit: boolean): void {", 1)

# helper paramIsOne
anchor = "  /** Cheap content stamp of omni.ja (length + sampled bytes) for cache gating. */"
assert s.count(anchor) == 1
s = s.replace(anchor, """  private paramIsOne(want: Want, key: string): boolean {
    try {
      const params: Record<string, Object> | undefined = want.parameters;
      if (params === undefined) {
        return false;
      }
      const value: Object | undefined = params[key];
      return value !== undefined && value.toString() === '1';
    } catch (error) {
      return false;
    }
  }

""" + anchor)

# init call: bench page + nojit switch
old_init = "      GeckoViewBoot.init('https://example.com/', dir);"
assert s.count(old_init) == 1
new_init = """      let startUrl: string = 'https://example.com/';
      if (perf) {
        const benchPath: string = this.context.filesDir + '/bench.html';
        try {
          const benchFd = fs.openSync(benchPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
          fs.writeSync(benchFd.fd, BENCH_PAGE_HTML);
          fs.closeSync(benchFd);
          hilog.info(DOMAIN, 'GeckoBoot', 'bench page written: %{public}s', benchPath);
        } catch (benchError) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'bench write failed: %{public}s', JSON.stringify(benchError));
        }
        startUrl = 'file://' + benchPath;
      }
      const engineArgs: string = nojit ? '--airweb-force-no-jit' : '';
      hilog.info(DOMAIN, 'GeckoBoot', 'engine start url=%{public}s args=%{public}s', startUrl, engineArgs);
      GeckoViewBoot.init(startUrl, dir, engineArgs);"""
s = s.replace(old_init, new_init)
io.open(p, 'w', encoding='utf-8').write(s)
print('EntryAbility parametrised')
