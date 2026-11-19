import { AbilityConstant, ConfigurationConstant, UIAbility, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';
import { fileIo as fs } from '@kit.CoreFileKit';
import { GeckoViewBoot, GeckoViewHandlers } from 'gecko';
import { GeckoEngine } from 'gecko';
import { SessionStore } from '../service/SessionStore';

const DOMAIN = 0x0000;





const BENCH_PAGE_HTML: string = '<html><head><title>bench</title></head><body><script>function ms(f){var t=performance.now();f();return Math.round(performance.now()-t);}function fib(n){return n<2?n:fib(n-1)+fib(n-2);}function run(){var r=[];for(var k=0;k<3;k++){var a=ms(function(){fib(27);});var b=ms(function(){var o={x:0};for(var i=0;i<5000000;i++){o.x+=i;}});var c=ms(function(){var a=[];for(var i=0;i<1000000;i++){a.push(i);}a.map(function(v){return v*2;}).reduce(function(p,q){return p+q;},0);});var d=ms(function(){var s="";for(var i=0;i<50000;i++){s+="ab";}s.split("").join("");});r.push("fib="+a+",obj="+b+",arr="+c+",str="+d);}document.title="BENCH "+r.join(" | ");}setTimeout(run,800);</script></body></html>';


const DEMO_PAGE_HTML: string = '<html><head><title>P1 demo</title></head><body style="font-size:26px;padding:36px"><p><a href="https://example.com/">示例链接</a></p><p><a href="https://example.com/?blank=1" target="_blank">新标签链接</a></p><p><img id="img" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNDAiIGhlaWdodD0iMjQwIj48cmVjdCB3aWR0aD0iMjQwIiBoZWlnaHQ9IjI0MCIgZmlsbD0iIzRDNkZGRiIvPjxjaXJjbGUgY3g9IjEyMCIgY3k9IjEyMCIgcj0iNjAiIGZpbGw9IiNGRkQxNjYiLz48dGV4dCB4PSIxMjAiIHk9IjEzMCIgZm9udC1zaXplPSIyOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzEyMTIxQSI+SU1HPC90ZXh0Pjwvc3ZnPg==" width="240" height="240"></p><p><video id="v" src="__VIDEO__" autoplay loop muted playsinline controls width="640" height="360"></video></p><p><input type="file" id="f" style="font-size:26px;width:620px"></p><p><select id="s" style="font-size:26px;padding:10px"><option>AAA</option><option>BBB</option><option>CCC</option></select></p><p><button onclick="dl()" style="font-size:26px;padding:16px">下载测试</button></p><p><button onclick="fs()" style="font-size:26px;padding:16px">全屏测试</button></p><script>function dl(){var b=new Blob(["hello-download"],{type:"text/plain"});var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="hello.txt";document.body.appendChild(a);a.click();}function fs(){document.documentElement.requestFullscreen();}</script></body></html>';

export default class EntryAbility extends UIAbility {
  private titleSeq: number = 0;
  private menuSeq: number = 0;
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    try {
      this.context.getApplicationContext().setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET);
    } catch (err) {
      hilog.error(DOMAIN, 'testTag', 'Failed to set colorMode. Cause: %{public}s', JSON.stringify(err));
    }
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onCreate');
    const perf: boolean = this.paramIsOne(want, 'perf');
    const nojit: boolean = this.paramIsOne(want, 'nojit');
    const store: SessionStore = SessionStore.instance();
    store.configure(this.context.filesDir);
    const unclean: boolean = store.beginEngineRun();
    AppStorage.setOrCreate('engineUnclean', unclean);
    AppStorage.setOrCreate('skipResume', this.paramIsOne(want, 'noresume'));
    AppStorage.setOrCreate('debugCtxMenu', this.paramIsOne(want, 'ctxmenu'));
    AppStorage.setOrCreate('menuAuto', this.paramIsOne(want, 'menuauto'));
    AppStorage.setOrCreate('diagMode', this.paramIsOne(want, 'diag'));
    AppStorage.setOrCreate('softDecode', this.paramIsOne(want, 'swdecode'));
    try {
      const flag = `${this.context.filesDir}/hwdecode.off`;
      if (this.paramIsOne(want, 'swdecode')) {
        const f = fs.openSync(flag, fs.OpenMode.CREATE | fs.OpenMode.WRITE_ONLY);
        fs.closeSync(f);
      } else {
        fs.unlinkSync(flag);
      }
    } catch (e) {
      hilog.warn(DOMAIN, 'GeckoBoot', 'hwdecode flag failed: %{public}s', JSON.stringify(e));
    }
    hilog.info(DOMAIN, 'GeckoBoot', 'previous run unclean=%{public}s', `${unclean}`);
    hilog.info(DOMAIN, 'GeckoBoot', 'launch params perf=%{public}s nojit=%{public}s',
      `${perf}`, `${nojit}`);
    this.bootGecko(perf, nojit, this.stringParam(want, 'url'), this.paramIsOne(want, 'demo'), this.paramIsOne(want, 'menutest'));
  }

  /**
   * M2 headless bring-up: copy the GRE archive (omni.ja) out of the gecko HSP
   * rawfile into the app sandbox, then start XRE_main through libgeckoview.so.
   */
  private bootGecko(perf: boolean, nojit: boolean, overrideUrl: string, demo: boolean, menuTest: boolean): void {
    try {
      const moduleContext = this.context.createModuleContext('gecko');
      const bytes = moduleContext.resourceManager.getRawFileContentSync('omni.ja');
      const dir = this.context.filesDir + '/gecko';
      if (!fs.accessSync(dir)) {
        fs.mkdirSync(dir);
      }
      const target = dir + '/omni.ja';
      const file = fs.openSync(target, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
      fs.writeSync(file.fd, bytes.buffer as ArrayBuffer);
      fs.closeSync(file);
      hilog.info(DOMAIN, 'GeckoBoot', 'omni.ja copied bytes=%{public}d -> %{public}s', bytes.length, target);
      // Register ALL engine callbacks BEFORE starting XRE_main; publish events
      // through AppStorage for the UI (address bar / IME focus).
      const handlers: GeckoViewHandlers = {
        onUrl: (sessionId: string, url: string) => {
          AppStorage.setOrCreate('geckoUrl', url);
          AppStorage.setOrCreate('geckoSession', sessionId);
        },
        onPageLoad: (sessionId: string, state: string) => {
          AppStorage.setOrCreate('geckoPageLoad', state);
        },
        onProgress: (progress: number) => {
          AppStorage.setOrCreate('geckoProgress', progress);
        },
        onIme: (state: string) => {
          AppStorage.setOrCreate('geckoImeState', state);
        },
        onMenu: (json: string) => {
          this.menuSeq += 1;
          AppStorage.setOrCreate('geckoMenu', json);
          AppStorage.setOrCreate('geckoMenuSeq', this.menuSeq);
        },
        onDownload: (json: string) => {
          AppStorage.setOrCreate('geckoDownload', json);
        },
        onFilePicker: (json: string, callbackId: number) => {
          AppStorage.setOrCreate('geckoFilePicker', JSON.stringify({ id: callbackId, req: json }));
        },
        onFullscreen: (fullscreen: boolean) => {
          AppStorage.setOrCreate('geckoFullscreen', fullscreen);
        },
        onTitle: (title: string, url: string, session: string) => {
          if (title.length > 0 || session === '__opentab__' || session === '__scroll__') {
            // Sequence makes every event distinct even for equal titles.
            this.titleSeq += 1;
            AppStorage.setOrCreate('geckoTitleEvent', JSON.stringify({
              seq: this.titleSeq,
              session: session,
              title: title,
              url: url
            }));
          }
        }
      };
      GeckoViewBoot.registerAll(handlers);
      if (menuTest) {
        const sample: string = '{"menuId":9001,"title":"","anchor":{"x":260,"y":180,"w":0,"h":0},"items":[' +
          '{"kind":"item","id":1,"label":"刷新页面","accel":"Ctrl+R","disabled":false,"checked":false,"hidden":false,"items":[]},' +
          '{"kind":"item","id":2,"label":"复制链接","accel":"Ctrl+C","disabled":false,"checked":false,"hidden":false,"items":[]},' +
          '{"kind":"separator","id":0,"label":"","accel":"","disabled":false,"checked":false,"hidden":false,"items":[]},' +
          '{"kind":"checkbox","id":3,"label":"显示工具栏","accel":"","disabled":false,"checked":true,"hidden":false,"items":[]},' +
          '{"kind":"item","id":4,"label":"禁用项示例","accel":"","disabled":true,"checked":false,"hidden":false,"items":[]}' +
          ']}';
        setTimeout(() => {
          this.menuSeq += 1;
          AppStorage.setOrCreate('geckoMenu', sample);
          AppStorage.setOrCreate('geckoMenuSeq', this.menuSeq);
          hilog.info(DOMAIN, 'GeckoBoot', 'menu test payload injected');
        }, 2500);
      }
      // Port patch (nsAppRunner.cpp OHOS branch) appends "/omni.ja" to the
      // -greomni path, so we must pass the DIRECTORY, not the file.
      // Engine startup page. Tab 0 of the ArkTS tab strip is bound to this
      // engine browser index (0).
      // Only clear the Gecko chrome-script cache when omni.ja content changed,
      // so cold starts stay fast after the first run of a given build.
      const stamp: string = this.omniStamp(bytes);
      const stampFile = dir + '/omni.stamp';
      let previousStamp: string = '';
      try {
        if (fs.accessSync(stampFile)) {
          previousStamp = fs.readTextSync(stampFile).trim();
        }
      } catch (error) {
        previousStamp = '';
      }
      if (previousStamp !== stamp) {
        this.clearStartupCache(`${this.context.filesDir}/profile`);
        try {
          const stampFd = fs.openSync(stampFile, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
          fs.writeSync(stampFd.fd, stamp);
          fs.closeSync(stampFd);
          hilog.info(DOMAIN, 'GeckoBoot', 'omni stamp updated: %{public}s', stamp);
        } catch (error) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'stamp write failed: %{public}s', JSON.stringify(error));
        }
      } else {
        hilog.info(DOMAIN, 'GeckoBoot', 'omni unchanged, startupCache kept');
      }
      let startUrl: string = 'https://example.com/';
      if (demo) {
        // copy bundled test clip so the demo page has a local H.264 source
        const clipPath: string = this.context.filesDir + '/test720.mp4';
        try {
          const clip: Uint8Array = this.context.resourceManager.getRawFileContentSync('test720.mp4');
          const fd = fs.openSync(clipPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
          fs.writeSync(fd.fd, clip.buffer);
          fs.closeSync(fd);
        } catch (clipError) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'clip copy failed');
        }
        const demoHtml: string = DEMO_PAGE_HTML.replace('__VIDEO__', 'file://' + clipPath);
        const demoPath: string = this.context.filesDir + '/demo.html';
        try {
          const demoFd = fs.openSync(demoPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
          fs.writeSync(demoFd.fd, demoHtml);
          fs.closeSync(demoFd);
        } catch (demoError) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'demo write failed');
        }
        startUrl = 'file://' + demoPath;
      }
      if (overrideUrl.length > 0) {
        startUrl = overrideUrl;
        hilog.info(DOMAIN, 'GeckoBoot', 'url override: %{public}s', startUrl);
      }
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
      if (AppStorage.get<boolean>('diagMode') === true) {
        setTimeout(() => {
          const files: string[] = ['ohosdec.log', 'gecko_debug.txt'];
          for (let fi = 0; fi < files.length; fi++) {
            const tail: string = GeckoEngine.readLogTail(`${this.context.filesDir}/${files[fi]}`, 20000);
            for (let i = 0; i < tail.length; i += 1000) {
              hilog.info(DOMAIN, 'Diag', '%{public}s', tail.substring(i, i + 1000));
            }
          }
        }, 9000);
      }
      // Enable the port's native-menu overlay path once XPCOM/prefs are ready.
      setTimeout(() => {
        try {
          GeckoViewBoot.setBoolPref('ohos.menu.native_overlay', true);
    GeckoViewBoot.setBoolPref('media.ohos.hw_decode', !(AppStorage.get<boolean>('softDecode') === true));
          GeckoViewBoot.setBoolPref('ohos.menu.autotest', AppStorage.get<boolean>('menuAuto') === true);
          try {
            const codecs: string = GeckoEngine.codecProbe();
            hilog.info(DOMAIN, 'GeckoBoot', 'video decoders: %{public}s', codecs.substring(0, 1500));
          } catch (probeError) {
            hilog.warn(DOMAIN, 'GeckoBoot', 'codec probe failed');
          }
          hilog.info(DOMAIN, 'GeckoBoot', 'native menu pref enabled');
        } catch (menuPrefError) {
          hilog.warn(DOMAIN, 'GeckoBoot', 'native menu pref failed');
        }
      }, 3000);
      hilog.info(DOMAIN, 'GeckoBoot', 'engine start url=%{public}s args=%{public}s', startUrl, engineArgs);
      GeckoViewBoot.init(startUrl, dir, engineArgs);
    } catch (error) {
      hilog.error(DOMAIN, 'GeckoBoot', 'bootGecko failed: %{public}s', JSON.stringify(error));
    }
  }

  onDestroy(): void {
    SessionStore.instance().endEngineRun();
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy (clean exit marker cleared)');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    // Main window is created, set main page for this ability
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onWindowStageCreate');

    windowStage.loadContent('pages/BrowserPage', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err));
        return;
      }
      hilog.info(DOMAIN, 'testTag', 'Succeeded in loading the content.');
    });
  }

  onWindowStageDestroy(): void {
    // Main window is destroyed, release UI related resources
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onWindowStageDestroy');
  }

  onForeground(): void {
    // Ability has brought to foreground
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onForeground');
  }

  onBackground(): void {
    // Ability has back to background
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onBackground');
  }

  private stringParam(want: Want, key: string): string {
    try {
      const params: Record<string, Object> | undefined = want.parameters;
      if (params === undefined) {
        return '';
      }
      const value: Object | undefined = params[key];
      return value !== undefined ? value.toString() : '';
    } catch (error) {
      return '';
    }
  }

  private paramIsOne(want: Want, key: string): boolean {
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

  /** Cheap content stamp of omni.ja (length + sampled bytes) for cache gating. */
  private omniStamp(bytes: Uint8Array): string {
    let hash: number = 5381;
    const len: number = bytes.length;
    const head: number = Math.min(len, 16384);
    for (let i = 0; i < head; i++) {
      hash = (((hash * 33) | 0) + bytes[i]) | 0;
    }
    const tailStart: number = Math.max(0, len - 16384);
    for (let i = tailStart; i < len; i++) {
      hash = (((hash * 33) | 0) + bytes[i]) | 0;
    }
    return `${len}-${(hash >>> 0).toString(16)}`;
  }

  /**
   * Gecko caches compiled chrome scripts in <profile>/startupCache. That cache
   * survives app reinstall/rebuild, so edited omni.ja JS would be ignored.
   * Clearing it before XRE_main forces chrome scripts to be re-read from the
   * freshly unpacked omni.ja.
   */
  private clearStartupCache(profileDir: string): void {
    const cacheDir = profileDir + '/startupCache';
    try {
      if (fs.accessSync(cacheDir)) {
        this.removeDirRecursive(cacheDir);
        hilog.info(DOMAIN, 'GeckoBoot', 'startupCache cleared');
      }
    } catch (error) {
      hilog.warn(DOMAIN, 'GeckoBoot', 'startupCache cleanup failed: %{public}s', JSON.stringify(error));
    }
  }

  private removeDirRecursive(dir: string): void {
    const names: string[] = fs.listFileSync(dir);
    for (const name of names) {
      const child = dir + '/' + name;
      if (fs.statSync(child).isDirectory()) {
        this.removeDirRecursive(child);
      } else {
        fs.unlinkSync(child);
      }
    }
    fs.rmdirSync(dir);
  }
}

