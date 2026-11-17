/**
 * LocalAccountService - first-release account and data portability.
 *
 * Scope (plan.md D10): a purely local profile plus JSON import/export. No
 * password, no network, no Firefox Accounts. Firefox Sync is M7 and reuses
 * Mozilla application-services instead of this file.
 */

import { preferences } from '@kit.ArkData';
import { common } from '@kit.AbilityKit';
import { fileIo as fs, picker } from '@kit.CoreFileKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { BrowserDatabase } from '../data/BrowserDatabase';
import { SettingsRepository } from '../data/SettingsRepository';
import {
  Bookmark,
  BrowserDataExport,
  HistoryEntry,
  LocalAccount
} from '../model/BrowserModels';

const DOMAIN: number = 0x3204;
const TAG: string = 'LocalAccountService';
const STORE_NAME: string = 'browser_account';
const KEY_ACCOUNT_ID: string = 'browser.account.id';
const KEY_DISPLAY_NAME: string = 'browser.account.displayName';
const KEY_CREATED_AT: string = 'browser.account.createdAt';
const KEY_LAST_EXPORT: string = 'browser.account.lastExportAt';
const EXPORT_SCHEMA: number = 1;
const EXPORT_FILE_NAME: string = 'firefoxport-backup.json';

export class LocalAccountService {
  private store: preferences.Preferences | undefined = undefined;

  init(context: common.Context): void {
    if (this.store !== undefined) {
      return;
    }
    const options: preferences.Options = { name: STORE_NAME };
    this.store = preferences.getPreferencesSync(context, options);
  }

  private requireStore(): preferences.Preferences {
    const current = this.store;
    if (current === undefined) {
      throw new Error('LocalAccountService.init(context) must be called first');
    }
    return current;
  }

  hasAccount(): boolean {
    return this.getAccount() !== undefined;
  }

  getAccount(): LocalAccount | undefined {
    const store = this.requireStore();
    const accountId = store.getSync(KEY_ACCOUNT_ID, '') as string;
    if (accountId.length === 0) {
      return undefined;
    }
    const account = new LocalAccount();
    account.accountId = accountId;
    account.displayName = store.getSync(KEY_DISPLAY_NAME, '本地用户') as string;
    account.createdAt = store.getSync(KEY_CREATED_AT, 0) as number;
    account.lastExportAt = store.getSync(KEY_LAST_EXPORT, 0) as number;
    return account;
  }

  async createAccount(displayName: string): Promise<LocalAccount> {
    const account = LocalAccount.create(displayName);
    const store = this.requireStore();
    store.putSync(KEY_ACCOUNT_ID, account.accountId);
    store.putSync(KEY_DISPLAY_NAME, account.displayName);
    store.putSync(KEY_CREATED_AT, account.createdAt);
    await store.flush();
    hilog.info(DOMAIN, TAG, 'local account created');
    return account;
  }

  async removeAccount(): Promise<void> {
    const store = this.requireStore();
    store.deleteSync(KEY_ACCOUNT_ID);
    store.deleteSync(KEY_DISPLAY_NAME);
    store.deleteSync(KEY_CREATED_AT);
    store.deleteSync(KEY_LAST_EXPORT);
    await store.flush();
  }

  /** Builds the export payload from the data layer. */
  async buildExport(database: BrowserDatabase, settings: SettingsRepository, profileId: string): Promise<BrowserDataExport> {
    const payload = new BrowserDataExport();
    payload.schemaVersion = EXPORT_SCHEMA;
    payload.exportedAt = Date.now();
    payload.bookmarks = await database.listBookmarks(profileId);
    payload.history = await database.listHistory(profileId, 1000);
    payload.downloads = await database.listDownloads(profileId);
    payload.settings = settings.snapshot();
    return payload;
  }

  /** Saves the payload through the document picker. Returns the chosen uri. */
  async exportToFile(context: common.Context, payload: BrowserDataExport): Promise<string> {
    const options = new picker.DocumentSaveOptions();
    options.newFileNames = [EXPORT_FILE_NAME];
    const documentPicker = new picker.DocumentViewPicker(context);
    const uris: Array<string> = await documentPicker.save(options);
    if (uris.length === 0) {
      return '';
    }
    const json = JSON.stringify(payload);
    const file = fs.openSync(uris[0], fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE | fs.OpenMode.TRUNC);
    fs.writeSync(file.fd, json);
    fs.closeSync(file);

    const store = this.requireStore();
    store.putSync(KEY_LAST_EXPORT, Date.now());
    await store.flush();
    hilog.info(DOMAIN, TAG, 'export written');
    return uris[0];
  }

  /** Picks a JSON backup and merges bookmarks/history into the database. */
  async importFromFile(context: common.Context, database: BrowserDatabase, profileId: string): Promise<number> {
    const options = new picker.DocumentSelectOptions();
    options.maxSelectNumber = 1;
    const documentPicker = new picker.DocumentViewPicker(context);
    const uris: Array<string> = await documentPicker.select(options);
    if (uris.length === 0) {
      return 0;
    }
    const text = fs.readTextSync(uris[0]);
    const parsed = JSON.parse(text) as BrowserDataExport;
    const importedBookmarks: Array<Bookmark> = parsed.bookmarks !== undefined ? parsed.bookmarks : [];
    const importedHistory: Array<HistoryEntry> = parsed.history !== undefined ? parsed.history : [];

    let imported = 0;
    for (let index = 0; index < importedBookmarks.length; index++) {
      const source = importedBookmarks[index];
      const bookmark = Bookmark.create(profileId, source.url, source.title);
      await database.addBookmark(bookmark);
      imported += 1;
    }
    for (let index = 0; index < importedHistory.length; index++) {
      const source = importedHistory[index];
      const entry = HistoryEntry.create(profileId, source.url, source.title);
      await database.addHistory(entry);
      imported += 1;
    }
    hilog.info(DOMAIN, TAG, 'import finished: %{public}d rows', imported);
    return imported;
  }
}
