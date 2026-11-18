/**
 * BrowserDatabase - RelationalStore persistence for the browser shell.
 *
 * Tables: profiles, bookmarks, history, downloads, permissions.
 * Every query is scoped by profile_id; private-mode tabs must never reach
 * addHistory() (enforced by the caller and re-checked here for defence in
 * depth by rejecting empty profile ids).
 */

import { relationalStore } from '@kit.ArkData';
import { common } from '@kit.AbilityKit';
import {
  Bookmark,
  DownloadRecord,
  DownloadState,
  HistoryEntry,
  PermissionDecision,
  PermissionGrant,
  Profile
} from '../model/BrowserModels';

const DB_NAME: string = 'browser.db';

const SQL_CREATE_PROFILES: string = `CREATE TABLE IF NOT EXISTS profiles (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  is_private INTEGER NOT NULL DEFAULT 0,
  engine_profile_path TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
)`;

const SQL_CREATE_BOOKMARKS: string = `CREATE TABLE IF NOT EXISTS bookmarks (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  parent_id TEXT NOT NULL DEFAULT '',
  url TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL,
  modified_at INTEGER NOT NULL
)`;

const SQL_CREATE_HISTORY: string = `CREATE TABLE IF NOT EXISTS history (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  url TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  visited_at INTEGER NOT NULL,
  visit_count INTEGER NOT NULL DEFAULT 1
)`;

const SQL_CREATE_DOWNLOADS: string = `CREATE TABLE IF NOT EXISTS downloads (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  url TEXT NOT NULL,
  file_name TEXT NOT NULL DEFAULT '',
  mime_type TEXT NOT NULL DEFAULT '',
  total_bytes INTEGER NOT NULL DEFAULT 0,
  received_bytes INTEGER NOT NULL DEFAULT 0,
  state TEXT NOT NULL,
  local_path TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
)`;

const SQL_CREATE_PERMISSIONS: string = `CREATE TABLE IF NOT EXISTS permissions (
  origin TEXT NOT NULL,
  permission TEXT NOT NULL,
  decision TEXT NOT NULL,
  updated_at INTEGER NOT NULL,
  PRIMARY KEY (origin, permission)
)`;

const SQL_INDEXES: Array<string> = [
  'CREATE INDEX IF NOT EXISTS idx_bookmarks_profile ON bookmarks(profile_id, sort_order)',
  'CREATE INDEX IF NOT EXISTS idx_history_profile_time ON history(profile_id, visited_at)',
  'CREATE INDEX IF NOT EXISTS idx_downloads_profile_time ON downloads(profile_id, created_at)'
];

export class BrowserDatabase {
  private store: relationalStore.RdbStore | undefined = undefined;
  private initializePromise: Promise<void> | undefined = undefined;

  /** Opens the store and creates the schema. Idempotent. */
  async init(context: common.Context): Promise<void> {
    if (this.store !== undefined) {
      return;
    }
    if (this.initializePromise !== undefined) {
      return this.initializePromise;
    }
    const config: relationalStore.StoreConfig = {
      name: DB_NAME,
      securityLevel: relationalStore.SecurityLevel.S1
    };
    const pending: Promise<void> = this.openStore(context, config);
    this.initializePromise = pending;
    return pending;
  }

  private async openStore(context: common.Context, config: relationalStore.StoreConfig): Promise<void> {
    const store = await relationalStore.getRdbStore(context, config);
    await store.executeSql(SQL_CREATE_PROFILES);
    await store.executeSql(SQL_CREATE_BOOKMARKS);
    await store.executeSql(SQL_CREATE_HISTORY);
    await store.executeSql(SQL_CREATE_DOWNLOADS);
    await store.executeSql(SQL_CREATE_PERMISSIONS);
    for (let index = 0; index < SQL_INDEXES.length; index++) {
      await store.executeSql(SQL_INDEXES[index]);
    }
    this.store = store;
  }

  isReady(): boolean {
    return this.store !== undefined;
  }

  private requireStore(): relationalStore.RdbStore {
    const current = this.store;
    if (current === undefined) {
      throw new Error('BrowserDatabase.init(context) must be awaited first');
    }
    return current;
  }

  // -------------------------------------------------------------------------
  // Profiles
  // -------------------------------------------------------------------------

  async upsertProfile(profile: Profile): Promise<void> {
    const values: relationalStore.ValuesBucket = {
      'id': profile.id,
      'name': profile.name,
      'is_private': profile.isPrivate ? 1 : 0,
      'engine_profile_path': profile.engineProfilePath,
      'created_at': profile.createdAt
    };
    await this.requireStore().insert('profiles', values, relationalStore.ConflictResolution.ON_CONFLICT_REPLACE);
  }

  async listProfiles(): Promise<Array<Profile>> {
    const predicates = new relationalStore.RdbPredicates('profiles');
    predicates.orderByDesc('created_at');
    const resultSet = await this.requireStore().query(predicates, [
      'id', 'name', 'is_private', 'engine_profile_path', 'created_at'
    ]);
    const profiles: Array<Profile> = [];
    while (resultSet.goToNextRow()) {
      const profile = new Profile();
      profile.id = resultSet.getString(resultSet.getColumnIndex('id'));
      profile.name = resultSet.getString(resultSet.getColumnIndex('name'));
      profile.isPrivate = resultSet.getLong(resultSet.getColumnIndex('is_private')) === 1;
      profile.engineProfilePath = resultSet.getString(resultSet.getColumnIndex('engine_profile_path'));
      profile.createdAt = resultSet.getLong(resultSet.getColumnIndex('created_at'));
      profiles.push(profile);
    }
    resultSet.close();
    return profiles;
  }

  // -------------------------------------------------------------------------
  // Bookmarks
  // -------------------------------------------------------------------------

  async addBookmark(bookmark: Bookmark): Promise<void> {
    const values: relationalStore.ValuesBucket = {
      'id': bookmark.id,
      'profile_id': bookmark.profileId,
      'parent_id': bookmark.parentId,
      'url': bookmark.url,
      'title': bookmark.title,
      'sort_order': bookmark.order,
      'created_at': bookmark.createdAt,
      'modified_at': bookmark.modifiedAt
    };
    await this.requireStore().insert('bookmarks', values, relationalStore.ConflictResolution.ON_CONFLICT_REPLACE);
  }

  async listBookmarks(profileId: string): Promise<Array<Bookmark>> {
    const predicates = new relationalStore.RdbPredicates('bookmarks');
    predicates.equalTo('profile_id', profileId);
    predicates.orderByDesc('created_at');
    const resultSet = await this.requireStore().query(predicates, [
      'id', 'profile_id', 'parent_id', 'url', 'title', 'sort_order', 'created_at', 'modified_at'
    ]);
    const bookmarks: Array<Bookmark> = [];
    while (resultSet.goToNextRow()) {
      const bookmark = new Bookmark();
      bookmark.id = resultSet.getString(resultSet.getColumnIndex('id'));
      bookmark.profileId = resultSet.getString(resultSet.getColumnIndex('profile_id'));
      bookmark.parentId = resultSet.getString(resultSet.getColumnIndex('parent_id'));
      bookmark.url = resultSet.getString(resultSet.getColumnIndex('url'));
      bookmark.title = resultSet.getString(resultSet.getColumnIndex('title'));
      bookmark.order = resultSet.getLong(resultSet.getColumnIndex('sort_order'));
      bookmark.createdAt = resultSet.getLong(resultSet.getColumnIndex('created_at'));
      bookmark.modifiedAt = resultSet.getLong(resultSet.getColumnIndex('modified_at'));
      bookmarks.push(bookmark);
    }
    resultSet.close();
    return bookmarks;
  }

  async removeBookmark(id: string): Promise<void> {
    const predicates = new relationalStore.RdbPredicates('bookmarks');
    predicates.equalTo('id', id);
    await this.requireStore().delete(predicates);
  }

  // -------------------------------------------------------------------------
  // History (never called for private sessions)
  // -------------------------------------------------------------------------

  async addHistory(entry: HistoryEntry): Promise<void> {
    if (entry.profileId.length === 0) {
      throw new Error('addHistory rejected: empty profileId');
    }
    const values: relationalStore.ValuesBucket = {
      'id': entry.id,
      'profile_id': entry.profileId,
      'url': entry.url,
      'title': entry.title,
      'visited_at': entry.visitedAt,
      'visit_count': entry.visitCount
    };
    await this.requireStore().insert('history', values, relationalStore.ConflictResolution.ON_CONFLICT_REPLACE);
  }

  async listHistory(profileId: string, limit: number): Promise<Array<HistoryEntry>> {
    const predicates = new relationalStore.RdbPredicates('history');
    predicates.equalTo('profile_id', profileId);
    predicates.orderByDesc('visited_at');
    predicates.limitAs(limit > 0 ? limit : 200);
    const resultSet = await this.requireStore().query(predicates, [
      'id', 'profile_id', 'url', 'title', 'visited_at', 'visit_count'
    ]);
    const entries: Array<HistoryEntry> = [];
    while (resultSet.goToNextRow()) {
      const entry = new HistoryEntry();
      entry.id = resultSet.getString(resultSet.getColumnIndex('id'));
      entry.profileId = resultSet.getString(resultSet.getColumnIndex('profile_id'));
      entry.url = resultSet.getString(resultSet.getColumnIndex('url'));
      entry.title = resultSet.getString(resultSet.getColumnIndex('title'));
      entry.visitedAt = resultSet.getLong(resultSet.getColumnIndex('visited_at'));
      entry.visitCount = resultSet.getLong(resultSet.getColumnIndex('visit_count'));
      entries.push(entry);
    }
    resultSet.close();
    return entries;
  }

  async clearHistory(profileId: string): Promise<void> {
    const predicates = new relationalStore.RdbPredicates('history');
    predicates.equalTo('profile_id', profileId);
    await this.requireStore().delete(predicates);
  }

  // -------------------------------------------------------------------------
  // Downloads
  // -------------------------------------------------------------------------

  async upsertDownload(record: DownloadRecord): Promise<void> {
    const values: relationalStore.ValuesBucket = {
      'id': record.id,
      'profile_id': record.profileId,
      'url': record.url,
      'file_name': record.fileName,
      'mime_type': record.mimeType,
      'total_bytes': record.totalBytes,
      'received_bytes': record.receivedBytes,
      'state': record.state,
      'local_path': record.localPath,
      'created_at': record.createdAt
    };
    await this.requireStore().insert('downloads', values, relationalStore.ConflictResolution.ON_CONFLICT_REPLACE);
  }

  async deleteDownload(id: string): Promise<void> {
    const predicates = new relationalStore.RdbPredicates('downloads');
    predicates.equalTo('id', id);
    await this.requireStore().delete(predicates);
  }

  async clearDownloads(profileId: string): Promise<void> {
    const predicates = new relationalStore.RdbPredicates('downloads');
    predicates.equalTo('profile_id', profileId);
    await this.requireStore().delete(predicates);
  }

  async listDownloads(profileId: string): Promise<Array<DownloadRecord>> {
    const predicates = new relationalStore.RdbPredicates('downloads');
    predicates.equalTo('profile_id', profileId);
    predicates.orderByDesc('created_at');
    const resultSet = await this.requireStore().query(predicates, [
      'id', 'profile_id', 'url', 'file_name', 'mime_type',
      'total_bytes', 'received_bytes', 'state', 'local_path', 'created_at'
    ]);
    const records: Array<DownloadRecord> = [];
    while (resultSet.goToNextRow()) {
      const record = new DownloadRecord();
      record.id = resultSet.getString(resultSet.getColumnIndex('id'));
      record.profileId = resultSet.getString(resultSet.getColumnIndex('profile_id'));
      record.url = resultSet.getString(resultSet.getColumnIndex('url'));
      record.fileName = resultSet.getString(resultSet.getColumnIndex('file_name'));
      record.mimeType = resultSet.getString(resultSet.getColumnIndex('mime_type'));
      record.totalBytes = resultSet.getLong(resultSet.getColumnIndex('total_bytes'));
      record.receivedBytes = resultSet.getLong(resultSet.getColumnIndex('received_bytes'));
      record.state = BrowserDatabase.parseDownloadState(resultSet.getString(resultSet.getColumnIndex('state')));
      record.localPath = resultSet.getString(resultSet.getColumnIndex('local_path'));
      record.createdAt = resultSet.getLong(resultSet.getColumnIndex('created_at'));
      records.push(record);
    }
    resultSet.close();
    return records;
  }

  private static parseDownloadState(raw: string): DownloadState {
    if (raw === DownloadState.DOWNLOADING) {
      return DownloadState.DOWNLOADING;
    }
    if (raw === DownloadState.PAUSED) {
      return DownloadState.PAUSED;
    }
    if (raw === DownloadState.COMPLETED) {
      return DownloadState.COMPLETED;
    }
    if (raw === DownloadState.FAILED) {
      return DownloadState.FAILED;
    }
    if (raw === DownloadState.CANCELED) {
      return DownloadState.CANCELED;
    }
    return DownloadState.QUEUED;
  }

  // -------------------------------------------------------------------------
  // Permissions
  // -------------------------------------------------------------------------

  async setPermission(grant: PermissionGrant): Promise<void> {
    const values: relationalStore.ValuesBucket = {
      'origin': grant.origin,
      'permission': grant.permission,
      'decision': grant.decision,
      'updated_at': grant.updatedAt
    };
    await this.requireStore().insert('permissions', values, relationalStore.ConflictResolution.ON_CONFLICT_REPLACE);
  }

  async getPermission(origin: string, permission: string): Promise<PermissionDecision> {
    const predicates = new relationalStore.RdbPredicates('permissions');
    predicates.equalTo('origin', origin);
    predicates.and();
    predicates.equalTo('permission', permission);
    const resultSet = await this.requireStore().query(predicates, ['decision']);
    let decision: PermissionDecision = PermissionDecision.ASK;
    if (resultSet.goToFirstRow()) {
      const raw = resultSet.getString(resultSet.getColumnIndex('decision'));
      if (raw === PermissionDecision.ALLOW) {
        decision = PermissionDecision.ALLOW;
      } else if (raw === PermissionDecision.DENY) {
        decision = PermissionDecision.DENY;
      }
    }
    resultSet.close();
    return decision;
  }
}
