/**
 * Domain models for the browser shell (US4).
 *
 * Plain classes with real initial values: they are persisted through
 * BrowserDatabase/SettingsRepository and rendered by V1 components. No UI
 * decorators here so the same objects can be used off the UI thread.
 */

/** Tab lifecycle states (see plan.md Data Model transitions). */
export enum LoadingState {
  CREATED = 'created',
  LOADING = 'loading',
  LOADED = 'loaded',
  STOPPED = 'stopped',
  CRASHED = 'crashed',
  CLOSED = 'closed'
}

/** Download state machine. */
export enum DownloadState {
  QUEUED = 'queued',
  DOWNLOADING = 'downloading',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELED = 'canceled'
}

/** Site permission decision. */
export enum PermissionDecision {
  ASK = 'ask',
  ALLOW = 'allow',
  DENY = 'deny'
}

/** Browser profile; private profiles never persist history. */
export class Profile {
  id: string = '';
  name: string = '';
  isPrivate: boolean = false;
  engineProfilePath: string = '';
  createdAt: number = 0;

  static of(id: string, name: string, isPrivate: boolean, engineProfilePath: string): Profile {
    const profile = new Profile();
    profile.id = id;
    profile.name = name;
    profile.isPrivate = isPrivate;
    profile.engineProfilePath = engineProfilePath;
    profile.createdAt = Date.now();
    return profile;
  }
}

/** A single tab. `engineSessionId` maps to a Gecko session once M2 lands. */
export class TabModel {
  id: string = '';
  profileId: string = 'default';
  engineSessionId: string = '';
  url: string = '';
  title: string = '';
  favicon: string = '';
  loadingState: LoadingState = LoadingState.CREATED;
  historyIndex: number = 0;
  isPrivate: boolean = false;
  createdAt: number = 0;

  static create(id: string, profileId: string, isPrivate: boolean): TabModel {
    const tab = new TabModel();
    tab.id = id;
    tab.profileId = profileId;
    tab.isPrivate = isPrivate;
    tab.title = '新标签页';
    tab.loadingState = LoadingState.CREATED;
    tab.createdAt = Date.now();
    return tab;
  }

  displayTitle(): string {
    if (this.title.length > 0) {
      return this.title;
    }
    if (this.url.length > 0) {
      return this.url;
    }
    return '新标签页';
  }
}

/** Lightweight tab descriptor passed to TabBar (primitive fields only). */
export class TabChip {
  id: string = '';
  title: string = '';
  url: string = '';
  privateMode: boolean = false;

  static of(id: string, title: string, url: string, privateMode: boolean): TabChip {
    const chip = new TabChip();
    chip.id = id;
    chip.title = title;
    chip.url = url;
    chip.privateMode = privateMode;
    return chip;
  }
}

/** Bookmark with optional folder hierarchy. */
export class Bookmark {
  id: string = '';
  profileId: string = 'default';
  parentId: string = '';
  url: string = '';
  title: string = '';
  order: number = 0;
  createdAt: number = 0;
  modifiedAt: number = 0;

  static create(profileId: string, url: string, title: string): Bookmark {
    const bookmark = new Bookmark();
    bookmark.id = `bm_${Date.now()}_${Math.floor(Math.random() * 100000)}`;
    bookmark.profileId = profileId;
    bookmark.url = url;
    bookmark.title = title;
    bookmark.createdAt = Date.now();
    bookmark.modifiedAt = bookmark.createdAt;
    return bookmark;
  }
}

/** History row. Private tabs must never create these. */
export class HistoryEntry {
  id: string = '';
  profileId: string = 'default';
  url: string = '';
  title: string = '';
  visitedAt: number = 0;
  visitCount: number = 1;

  static create(profileId: string, url: string, title: string): HistoryEntry {
    const entry = new HistoryEntry();
    entry.id = `hs_${Date.now()}_${Math.floor(Math.random() * 100000)}`;
    entry.profileId = profileId;
    entry.url = url;
    entry.title = title;
    entry.visitedAt = Date.now();
    return entry;
  }
}

/** Download record. `localPath` is the app-sandbox file path. */
export class DownloadRecord {
  id: string = '';
  profileId: string = 'default';
  url: string = '';
  fileName: string = '';
  mimeType: string = '';
  totalBytes: number = 0;
  receivedBytes: number = 0;
  state: DownloadState = DownloadState.QUEUED;
  localPath: string = '';
  createdAt: number = 0;

  progressPercent(): number {
    if (this.totalBytes <= 0) {
      return 0;
    }
    const percent = (this.receivedBytes * 100) / this.totalBytes;
    return Math.min(100, Math.max(0, Math.round(percent)));
  }
}

/** Setting row (Preferences stores the same shape as key/value). */
export class SettingEntry {
  key: string = '';
  value: string = '';
  valueType: string = 'string';
  updatedAt: number = 0;
  schemaVersion: number = 1;
}

/** Per-origin permission grant. */
export class PermissionGrant {
  origin: string = '';
  permission: string = '';
  decision: PermissionDecision = PermissionDecision.ASK;
  updatedAt: number = 0;
}

/** Local account (first release): no password is stored, only a display name. */
export class LocalAccount {
  accountId: string = '';
  displayName: string = '';
  createdAt: number = 0;
  lastExportAt: number = 0;

  static create(displayName: string): LocalAccount {
    const account = new LocalAccount();
    account.accountId = `local_${Date.now()}`;
    account.displayName = displayName;
    account.createdAt = Date.now();
    return account;
  }
}

/** Import/export payload for local account data. */
export class BrowserDataExport {
  schemaVersion: number = 1;
  exportedAt: number = 0;
  bookmarks: Array<Bookmark> = [];
  history: Array<HistoryEntry> = [];
  downloads: Array<DownloadRecord> = [];
  settings: Array<SettingEntry> = [];
}
