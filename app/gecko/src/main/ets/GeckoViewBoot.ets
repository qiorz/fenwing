/**
 * GeckoViewBoot - M2/M3 facade over the community port's libgeckoview.so NAPI.
 *
 * Contract notes (verified against ports/ohos/geckoview.cpp):
 *  - URL / pageLoad callbacks are invoked as (sessionId, value) -- two args;
 *  - progress callback is a single integer;
 *  - IME callback is a single string ("show"/"hide");
 *  - initFirefox() must be the only caller of XRE_GetBootstrap (one-shot API);
 *  - resourceDir must be the sandbox DIRECTORY containing omni.ja.
 */

import geckoview from 'libgeckoview.so';
import { hilog } from '@kit.PerformanceAnalysisKit';

const DOMAIN: number = 0x3204;
const TAG: string = 'GeckoViewBoot';

export interface GeckoViewHandlers {
  onUrl?: (sessionId: string, url: string) => void;
  onPageLoad?: (sessionId: string, state: string) => void;
  onProgress?: (progress: number) => void;
  onFirstComposite?: () => void;
  onTerminate?: () => void;
  onIme?: (state: string) => void;
  onTitle?: (title: string, url: string, session: string) => void;
  onDownload?: (json: string) => void;
  onFilePicker?: (json: string, callbackId: number) => void;
  onFullscreen?: (fullscreen: boolean) => void;
}

export class GeckoViewBoot {
  /** Registers all engine callbacks. Call BEFORE init() so nothing is missed. */
  static registerAll(handlers: GeckoViewHandlers): void {
    try {
      geckoview.registerURLcallback((sessionId: string, url: string) => {
        hilog.info(DOMAIN, TAG, 'url session=%{public}s url=%{public}s', sessionId, url);
        if (handlers.onUrl !== undefined) {
          handlers.onUrl(sessionId, url);
        }
      });
      geckoview.registerPageLoadCallback((sessionId: string, state: string) => {
        hilog.info(DOMAIN, TAG, 'pageLoad session=%{public}s state=%{public}s', sessionId, state);
        if (handlers.onPageLoad !== undefined) {
          handlers.onPageLoad(sessionId, state);
        }
      });
      geckoview.registerProgressCallback((progress: number) => {
        if (handlers.onProgress !== undefined) {
          handlers.onProgress(progress);
        }
      });
      geckoview.registerFirstCompositeCallback(() => {
        hilog.info(DOMAIN, TAG, 'first-composite');
        if (handlers.onFirstComposite !== undefined) {
          handlers.onFirstComposite();
        }
      });
      geckoview.registerTerminateCallback(() => {
        hilog.warn(DOMAIN, TAG, 'gecko terminated');
        if (handlers.onTerminate !== undefined) {
          handlers.onTerminate();
        }
      });      geckoview.registerTabStateCallback((json: string) => {
        try {
          const payload: TabTitlePayload = JSON.parse(json) as TabTitlePayload;
          const title: string = payload.title !== undefined ? payload.title : '';
          const url: string = payload.url !== undefined ? payload.url : '';
          const session: string = payload.session !== undefined ? payload.session : '';
          if (title.length === 0 && url.length === 0) {
            return;
          }
          hilog.info(DOMAIN, TAG, 'title session=%{public}s title=%{public}s', session, title);
          if (handlers.onTitle !== undefined) {
            handlers.onTitle(title, url, session);
          }
        } catch (error) {
          hilog.warn(DOMAIN, TAG, 'tab-state parse failed: %{public}s', JSON.stringify(error));
        }
      });
      if (handlers.onIme !== undefined) {
        geckoview.registerIMECallback((state: string) => {
          hilog.info(DOMAIN, TAG, 'IME state=%{public}s', state);
          if (handlers.onIme !== undefined) {
            handlers.onIme(state);
          }
        });
      }
      if (handlers.onDownload !== undefined) {
        geckoview.registerDownloadCallback((json: string) => {
          if (handlers.onDownload !== undefined) {
            handlers.onDownload(json);
          }
        });
      }
      if (handlers.onFilePicker !== undefined) {
        geckoview.registerFilePickerCallback((json: string, callbackId: number) => {
          if (handlers.onFilePicker !== undefined) {
            handlers.onFilePicker(json, callbackId);
          }
        });
      }
      if (handlers.onFullscreen !== undefined) {
        geckoview.registerFullscreenCallback((fullscreen: boolean) => {
          if (handlers.onFullscreen !== undefined) {
            handlers.onFullscreen(fullscreen);
          }
        });
      }
      hilog.info(DOMAIN, TAG, 'callbacks registered');
    } catch (error) {
      hilog.error(DOMAIN, TAG, 'registerAll failed: %{public}s', JSON.stringify(error));
    }
  }

  /** Starts XRE_main with the GRE archive at resourceDir. */
  static init(url: string, resourceDir: string, commandlineArgs: string = ''): void {
    hilog.info(DOMAIN, TAG, 'initFirefox url=%{public}s resourceDir=%{public}s args=%{public}s',
      url, resourceDir, commandlineArgs);
    geckoview.initFirefox({
      url: url,
      resourceDir: resourceDir,
      commandlineArgs: commandlineArgs,
      uiMode: 'classic'
    });
    hilog.info(DOMAIN, TAG, 'initFirefox dispatched');
  }

  static loadUrl(url: string): void {
    hilog.info(DOMAIN, TAG, 'loadUrl %{public}s', url);
    geckoview.loadURL(url);
  }

  /**
   * Creates an engine browser (tab) for sessionId. Engine index 0 is the
   * initial browser created by geckoview.js at startup; new tabs must start
   * from 1.
   */
  static createSession(sessionId: number, url: string): void {
    hilog.info(DOMAIN, TAG, 'createSession id=%{public}d url=%{public}s', sessionId, url);
    geckoview.createSession(sessionId, url);
  }

  static switchToSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'switchToSession id=%{public}d', sessionId);
    geckoview.switchToSession(sessionId);
  }

  static closeSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'closeSession id=%{public}d', sessionId);
    geckoview.closeSession(sessionId);
  }

  static loadUrlForSession(sessionId: number, url: string): void {
    hilog.info(DOMAIN, TAG, 'loadUrlForSession id=%{public}d url=%{public}s', sessionId, url);
    geckoview.loadURLForSession(sessionId, url);
  }

  /** Forces the widget to repaint (used after tab switches). */
  static forceRepaint(): void {
    geckoview.forceRepaint();
  }

  static goBackForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'goBack session=%{public}d', sessionId);
    geckoview.goBackForSession(sessionId);
  }

  static goForwardForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'goForward session=%{public}d', sessionId);
    geckoview.goForwardForSession(sessionId);
  }

  static reloadForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'reloadSession session=%{public}d', sessionId);
    geckoview.reloadForSession(sessionId);
  }

  static stopForSession(sessionId: number): void {
    hilog.info(DOMAIN, TAG, 'stopSession session=%{public}d', sessionId);
    geckoview.stopForSession(sessionId);
  }

  /** Session history of the active engine browser; throws when unavailable. */
  static sessionHistory(): SessionHistoryReport {
    const report = new SessionHistoryReport();
    const raw: SessionHistoryReport = geckoview.getSessionHistory() as SessionHistoryReport;
    report.index = raw.index;
    report.count = raw.count;
    return report;
  }

  static reload(): void {
    geckoview.reload();
  }

  static goBack(): void {
    geckoview.goBack();
  }

  static goForward(): void {
    geckoview.goForward();
  }

  /** Surface pixel size reported by the engine (0x0 before first surface). */
  static surfaceSize(): SurfaceSizeReport {
    const report = new SurfaceSizeReport();
    try {
      const size: SurfaceSizeReport = geckoview.getSurfaceSize() as SurfaceSizeReport;
      report.width = size.width;
      report.height = size.height;
    } catch (error) {
      report.width = 0;
      report.height = 0;
    }
    return report;
  }

  static touch(action: number, x: number, y: number, time: number): void {
    geckoview.touchEvent(action, x, y, time);
  }

  static mouseMove(x: number, y: number): void {
    geckoview.mouseMove(x, y);
  }

  static mouseDown(x: number, y: number, button: number): void {
    geckoview.mouseDown(x, y, button);
  }

  static mouseUp(x: number, y: number, button: number): void {
    geckoview.mouseUp(x, y, button);
  }

  static scroll(dx: number, dy: number, x: number, y: number): void {
    geckoview.scroll(dx, dy, x, y);
  }

  static key(action: number, keyCode: number, modifiers: number): void {
    geckoview.dispatchKeyEvent(action, keyCode, modifiers);
  }

  static insertText(text: string): void {
    geckoview.insertText(text);
  }

  static deleteText(length: number): void {
    geckoview.deleteText(length);
  }

  static resolveFilePicker(callbackId: number, result: number, path: string): void {
    hilog.info(DOMAIN, TAG, 'resolveFilePicker id=%{public}d result=%{public}d', callbackId, result);
    geckoview.resolveFilePicker(callbackId, result, path);
  }

  static exitFullscreen(): void {
    geckoview.exitFullscreen();
  }

  static findInPage(query: string, backward: boolean, matchCase: boolean): void {
    hilog.info(DOMAIN, TAG, 'findInPage %{public}s', query);
    geckoview.findInPage(query, backward ? 1 : 0, matchCase ? 1 : 0);
  }

  static setFullZoom(zoom: number): void {
    hilog.info(DOMAIN, TAG, 'setFullZoom %{public}f', zoom);
    geckoview.setFullZoom(zoom);
  }
}

/** Envelope pushed by geckoview.js for active-tab title/url sync. */
export interface TabTitlePayload {
  session?: string;
  title?: string;
  url?: string;
}

/** Plain mirror of the native surface-size payload. */
export class SurfaceSizeReport {
  width: number = 0;
  height: number = 0;
}

/** Session history position/count of the active engine browser. */
export class SessionHistoryReport {
  index: number = 0;
  count: number = 0;
}
