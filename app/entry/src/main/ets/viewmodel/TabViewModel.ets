/**
 * TabViewModel - tab lifecycle and navigation intents.
 *
 * The view model owns the tab list and the active tab. It never touches the
 * engine directly: BrowserPage forwards navigation to GeckoService, which is
 * still an M0 stub. Components re-read `snapshot()` after `onChange` fires,
 * which keeps V1 state updates simple and predictable.
 */

import { LoadingState, TabModel } from '../model/BrowserModels';

const ABOUT_NEW_TAB: string = 'about:newtab';
const ABOUT_HOME: string = 'about:home';
const ABOUT_SEARCH: string = 'about:search';

export class TabViewModel {
  private tabs: Array<TabModel> = [];
  private activeTabId: string = '';
  private profileId: string = 'default';
  private privateMode: boolean = false;
  private sequence: number = 0;

  /** Set by the page; called after every mutation. */
  onChange: () => void = () => {
  };

  configure(profileId: string, privateMode: boolean): void {
    this.profileId = profileId;
    this.privateMode = privateMode;
  }

  isPrivateMode(): boolean {
    return this.privateMode;
  }

  getProfileId(): string {
    return this.profileId;
  }

  setPrivateMode(enabled: boolean): void {
    if (this.privateMode === enabled) {
      return;
    }
    this.privateMode = enabled;
    // Entering or leaving private mode drops the previous session entirely:
    // private tabs must not leak into the normal profile and vice versa.
    const keep: Array<TabModel> = [];
    this.tabs = keep;
    this.activeTabId = '';
    this.createTab(ABOUT_NEW_TAB);
  }

  createTab(url: string): TabModel {
    this.sequence += 1;
    const tabId = `tab_${Date.now()}_${this.sequence}`;
    const tab = TabModel.create(tabId, this.profileId, this.privateMode);
    tab.url = url.length > 0 ? url : ABOUT_NEW_TAB;
    if (this.tabs.length === 0) {
      this.tabs.push(tab);
      this.activeTabId = tab.id;
    } else {
      this.tabs.push(tab);
      this.activeTabId = tab.id;
    }
    this.notify();
    return tab;
  }

  closeTab(tabId: string): void {
    const remaining: Array<TabModel> = [];
    for (let index = 0; index < this.tabs.length; index++) {
      if (this.tabs[index].id !== tabId) {
        remaining.push(this.tabs[index]);
      }
    }
    this.tabs = remaining;
    if (this.activeTabId === tabId) {
      if (this.tabs.length > 0) {
        this.activeTabId = this.tabs[this.tabs.length - 1].id;
      } else {
        this.activeTabId = '';
      }
    }
    if (this.tabs.length === 0) {
      this.createTab(ABOUT_NEW_TAB);
      return;
    }
    this.notify();
  }

  activateTab(tabId: string): void {
    const tab = this.findById(tabId);
    if (tab === undefined) {
      return;
    }
    this.activeTabId = tabId;
    this.notify();
  }

  navigate(tabId: string, url: string): void {
    const tab = this.findById(tabId);
    if (tab === undefined) {
      return;
    }
    tab.url = url;
    tab.loadingState = LoadingState.LOADING;
    this.notify();
  }

  /** Updates the tab URL without touching the loading state (engine URL sync). */
  setUrl(tabId: string, url: string): void {
    const tab = this.findById(tabId);
    if (tab === undefined) {
      return;
    }
    if (tab.url === url) {
      return;
    }
    tab.url = url;
    this.notify();
  }

  markLoaded(tabId: string, title: string): void {
    const tab = this.findById(tabId);
    if (tab === undefined) {
      return;
    }
    tab.title = title;
    tab.loadingState = LoadingState.LOADED;
    this.notify();
  }

  markStopped(tabId: string): void {
    const tab = this.findById(tabId);
    if (tab === undefined) {
      return;
    }
    tab.loadingState = LoadingState.STOPPED;
    this.notify();
  }

  markCrashed(tabId: string): void {
    const tab = this.findById(tabId);
    if (tab === undefined) {
      return;
    }
    tab.loadingState = LoadingState.CRASHED;
    this.notify();
  }

  snapshot(): Array<TabModel> {
    return this.tabs.slice();
  }

  getActiveTab(): TabModel | undefined {
    return this.findById(this.activeTabId);
  }

  getActiveTabId(): string {
    return this.activeTabId;
  }

  tabCount(): number {
    return this.tabs.length;
  }

  /** Resolves user input to an internal URL. External resolution is M4. */
  static normalizeInput(input: string, searchEngineName: string): string {
    const trimmed = input.trim();
    if (trimmed.length === 0) {
      return ABOUT_NEW_TAB;
    }
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://') ||
      trimmed.startsWith('about:') || trimmed.startsWith('file://')) {
      return trimmed;
    }
    if (trimmed.startsWith('/') || trimmed.startsWith('./')) {
      return `file://${trimmed}`;
    }
    const hasDot = trimmed.indexOf('.') >= 0;
    const hasSpace = trimmed.indexOf(' ') >= 0;
    if (!hasDot || hasSpace) {
      // Search intent. The engine resolves about:search in M4; keeping it
      // internal avoids hardcoding a third-party provider in the UI layer.
      return `${ABOUT_SEARCH}?engine=${encodeURIComponent(searchEngineName)}&q=${encodeURIComponent(trimmed)}`;
    }
    return `https://${trimmed}`;
  }

  static newTabUrl(): string {
    return ABOUT_NEW_TAB;
  }

  static homeUrl(): string {
    return ABOUT_HOME;
  }

  private findById(tabId: string): TabModel | undefined {
    for (let index = 0; index < this.tabs.length; index++) {
      if (this.tabs[index].id === tabId) {
        return this.tabs[index];
      }
    }
    return undefined;
  }

  private notify(): void {
    this.onChange();
  }
}
