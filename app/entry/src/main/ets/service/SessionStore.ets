/**
 * SessionStore - tiny JSON persistence for crash recovery (P0).
 *
 * Files (all under the app sandbox filesDir):
 *  - session.json : last known tab list + active index (written on every change)
 *  - engine.run   : marker written before XRE_main; removed on graceful exit.
 *                   If it exists at the next launch, the previous run died
 *                   uncleanly (crash / OOM kill / force-stop).
 *
 * The store is deliberately synchronous and tiny: it is called from UI paths
 * that already run on the ArkTS main thread and must never block.
 */

import { fileIo as fs } from '@kit.CoreFileKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

const DOMAIN: number = 0x0000;
const TAG: string = 'SessionStore';

export class SavedTab {
  url: string = '';
  title: string = '';
}

export class SavedSession {
  version: number = 1;
  tabs: Array<SavedTab> = [];
  activeIndex: number = 0;
}

export class SessionStore {
  private static sInstance: SessionStore | undefined = undefined;

  private filesDir: string = '';
  private sessionPath: string = '';
  private markerPath: string = '';

  static instance(): SessionStore {
    if (SessionStore.sInstance === undefined) {
      SessionStore.sInstance = new SessionStore();
    }
    return SessionStore.sInstance;
  }

  configure(filesDir: string): void {
    this.filesDir = filesDir;
    this.sessionPath = filesDir + '/session.json';
    this.markerPath = filesDir + '/engine.run';
  }

  /** True when the previous run did not shut down gracefully. */
  beginEngineRun(): boolean {
    let unclean: boolean = false;
    try {
      unclean = fs.accessSync(this.markerPath);
    } catch (error) {
      unclean = false;
    }
    try {
      const fd = fs.openSync(this.markerPath, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
      fs.writeSync(fd.fd, `${Date.now()}`);
      fs.closeSync(fd);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'marker write failed: %{public}s', JSON.stringify(error));
    }
    return unclean;
  }

  /** Graceful shutdown: marker removal means "clean exit" for next launch. */
  endEngineRun(): void {
    try {
      if (fs.accessSync(this.markerPath)) {
        fs.unlinkSync(this.markerPath);
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'marker clear failed: %{public}s', JSON.stringify(error));
    }
  }

  save(session: SavedSession): void {
    try {
      const tmp: string = this.sessionPath + '.tmp';
      const fd = fs.openSync(tmp, fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE | fs.OpenMode.TRUNC);
      fs.writeSync(fd.fd, JSON.stringify(session));
      fs.closeSync(fd);
      if (fs.accessSync(this.sessionPath)) {
        fs.unlinkSync(this.sessionPath);
      }
      fs.renameSync(tmp, this.sessionPath);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'session save failed: %{public}s', JSON.stringify(error));
    }
  }

  load(): SavedSession | undefined {
    try {
      if (!fs.accessSync(this.sessionPath)) {
        return undefined;
      }
      const text: string = fs.readTextSync(this.sessionPath);
      if (text.length === 0) {
        return undefined;
      }
      const parsed = JSON.parse(text) as SavedSession;
      if (parsed === null || parsed === undefined || !Array.isArray(parsed.tabs) || parsed.tabs.length === 0) {
        return undefined;
      }
      return parsed;
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'session load failed: %{public}s', JSON.stringify(error));
      return undefined;
    }
  }
}
