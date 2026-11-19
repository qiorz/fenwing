/**
 * SettingsRepository - typed access to Preferences.
 *
 * Key namespace: `browser.<domain>.<key>` (plan.md storage contract).
 * Every write bumps `browser.schema.version` awareness; readers always pass a
 * default so a fresh install never sees undefined.
 */

import { preferences } from '@kit.ArkData';
import { common } from '@kit.AbilityKit';
import { SettingEntry } from '../model/BrowserModels';

export class SettingsKeys {
  static readonly SCHEMA_VERSION: string = 'browser.schema.version';
  static readonly SEARCH_ENGINE: string = 'browser.general.searchEngine';
  static readonly HOMEPAGE: string = 'browser.general.homepage';
  static readonly JAVASCRIPT: string = 'browser.content.javascript';
  static readonly IMAGES: string = 'browser.content.images';
  static readonly DO_NOT_TRACK: string = 'browser.privacy.doNotTrack';
  static readonly DEFAULT_PRIVATE: string = 'browser.privacy.defaultPrivate';
  static readonly THEME: string = 'browser.appearance.theme';
  static readonly DOWNLOAD_DIR: string = 'browser.download.directory';
  static readonly ENGINE_LOG_LEVEL: string = 'browser.engine.logLevel';
  static readonly USER_AGENT: string = 'browser.general.userAgent';
}

const STORE_NAME: string = 'browser_settings';
const CURRENT_SCHEMA: number = 1;

export class SettingsRepository {
  private store: preferences.Preferences | undefined = undefined;

  isReady(): boolean {
    return this.store !== undefined;
  }

  init(context: common.Context): void {
    if (this.store !== undefined) {
      return;
    }
    const options: preferences.Options = { name: STORE_NAME };
    this.store = preferences.getPreferencesSync(context, options);
    const schemaVersion = this.store.getSync(SettingsKeys.SCHEMA_VERSION, 0) as number;
    if (schemaVersion < CURRENT_SCHEMA) {
      this.store.putSync(SettingsKeys.SCHEMA_VERSION, CURRENT_SCHEMA);
      this.store.flush();
    }
  }

  private requireStore(): preferences.Preferences {
    const current = this.store;
    if (current === undefined) {
      throw new Error('SettingsRepository.init(context) must be called first');
    }
    return current;
  }

  getSearchEngine(): string {
    return this.requireStore().getSync(SettingsKeys.SEARCH_ENGINE, 'DuckDuckGo') as string;
  }

  getUserAgentMode(): string {
    return this.requireStore().getSync(SettingsKeys.USER_AGENT, 'harmony') as string;
  }

  async setUserAgentMode(value: string): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.USER_AGENT, value);
    await store.flush();
  }

  async setSearchEngine(value: string): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.SEARCH_ENGINE, value);
    await store.flush();
  }

  getHomepage(): string {
    return this.requireStore().getSync(SettingsKeys.HOMEPAGE, 'about:home') as string;
  }

  async setHomepage(value: string): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.HOMEPAGE, value);
    await store.flush();
  }

  isJavascriptEnabled(): boolean {
    return this.requireStore().getSync(SettingsKeys.JAVASCRIPT, true) as boolean;
  }

  async setJavascriptEnabled(enabled: boolean): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.JAVASCRIPT, enabled);
    await store.flush();
  }

  areImagesEnabled(): boolean {
    return this.requireStore().getSync(SettingsKeys.IMAGES, true) as boolean;
  }

  async setImagesEnabled(enabled: boolean): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.IMAGES, enabled);
    await store.flush();
  }

  isDoNotTrackEnabled(): boolean {
    return this.requireStore().getSync(SettingsKeys.DO_NOT_TRACK, true) as boolean;
  }

  async setDoNotTrackEnabled(enabled: boolean): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.DO_NOT_TRACK, enabled);
    await store.flush();
  }

  isPrivateByDefault(): boolean {
    return this.requireStore().getSync(SettingsKeys.DEFAULT_PRIVATE, false) as boolean;
  }

  async setPrivateByDefault(enabled: boolean): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.DEFAULT_PRIVATE, enabled);
    await store.flush();
  }

  getTheme(): string {
    return this.requireStore().getSync(SettingsKeys.THEME, 'dark') as string;
  }

  async setTheme(value: string): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.THEME, value);
    await store.flush();
  }

  getDownloadDirectory(): string {
    return this.requireStore().getSync(SettingsKeys.DOWNLOAD_DIR, '') as string;
  }

  async setDownloadDirectory(value: string): Promise<void> {
    const store = this.requireStore();
    store.putSync(SettingsKeys.DOWNLOAD_DIR, value);
    await store.flush();
  }

  getSchemaVersion(): number {
    return this.requireStore().getSync(SettingsKeys.SCHEMA_VERSION, CURRENT_SCHEMA) as number;
  }

  /** Flattened snapshot used by export. */
  snapshot(): Array<SettingEntry> {
    const store = this.requireStore();
    const entries: Array<SettingEntry> = [];
    const keys: Array<string> = [
      SettingsKeys.SEARCH_ENGINE,
      SettingsKeys.HOMEPAGE,
      SettingsKeys.JAVASCRIPT,
      SettingsKeys.IMAGES,
      SettingsKeys.DO_NOT_TRACK,
      SettingsKeys.DEFAULT_PRIVATE,
      SettingsKeys.THEME,
      SettingsKeys.DOWNLOAD_DIR,
      SettingsKeys.ENGINE_LOG_LEVEL
    ];
    const defaults: Array<preferences.ValueType> = ['DuckDuckGo', 'about:home', true, true, true, false, 'dark', '', 'info'];
    for (let index = 0; index < keys.length; index++) {
      const entry = new SettingEntry();
      entry.key = keys[index];
      entry.value = `${store.getSync(keys[index], defaults[index])}`;
      entry.valueType = typeof defaults[index];
      entry.updatedAt = Date.now();
      entry.schemaVersion = CURRENT_SCHEMA;
      entries.push(entry);
    }
    return entries;
  }
}
