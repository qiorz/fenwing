/**
 * BrowserPage - browser shell MVP (US4).
 *
 * Layout: address bar -> content area -> tab strip -> optional data panel.
 *
 * Engine integration: GeckoService is still an M0 bridge, so navigation shows
 * an explicit placeholder and surfaces the UNSUPPORTED reason. The shell is
 * fully usable for tabs, bookmarks, history, downloads, settings and private
 * mode, and writing history is hard-gated on private mode (T048).
 */

import { common } from '@kit.AbilityKit';
import { picker, fileIo as p1fs, fileUri } from '@kit.CoreFileKit';
import { window as p1window } from '@kit.ArkUI';
import { router } from '@kit.ArkUI';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { GeckoViewBoot } from 'gecko';
import { SavedSession, SavedTab, SessionStore } from '../service/SessionStore';
import { AddressBar } from '../components/AddressBar';
import { TabBar } from '../components/TabBar';
import { GeckoSurface } from '../components/GeckoSurface';
import { BookmarksView } from '../views/BookmarksView';
import { HistoryView } from '../views/HistoryView';
import { DownloadsView } from '../views/DownloadsView';
import { SettingsView } from '../views/SettingsView';
import { GeckoService } from '../service/GeckoService';
import { SettingsRepository } from '../data/SettingsRepository';
import { BrowserDatabase } from '../data/BrowserDatabase';
import { LocalAccountService } from '../service/LocalAccountService';
import { TabViewModel } from '../viewmodel/TabViewModel';
import {
  Bookmark,
  DownloadRecord,
  DownloadState,
  HistoryEntry,
  LoadingState,
  TabChip
} from '../model/BrowserModels';
import { EngineAvailability, SessionConfig } from '../common/GeckoTypes';
import { GeckoError, toGeckoError } from '../common/GeckoErrors';

const DOMAIN: number = 0x3205;
const TAG: string = 'BrowserPage';
const PROFILE_ID: string = 'default';
const PANEL_NONE: string = 'none';
const PANEL_BOOKMARKS: string = 'bookmarks';
const PANEL_HISTORY: string = 'history';
const PANEL_DOWNLOADS: string = 'downloads';
const PANEL_SETTINGS: string = 'settings';

@Entry
@Component
struct BrowserPage {
  @State private tabs: Array<TabChip> = [];
  @State private activeTabId: string = '';
  @State private currentUrl: string = '';
  @StorageProp('geckoUrl') @Watch('onGeckoUrlChanged') geckoUrl: string = '';
  @StorageProp('geckoSession') geckoSession: string = '';
  @StorageProp('geckoPageLoad') @Watch('onGeckoPageLoadChanged') geckoPageLoad: string = '';
  @StorageProp('geckoTitleEvent') @Watch('onGeckoTitleChanged') geckoTitleEvent: string = '';
  @State private canGoBack: boolean = false;
  @State private canGoForward: boolean = false;
  @StorageProp('geckoDownload') @Watch('onDownloadEvent') geckoDownload: string = '';
  @StorageProp('geckoFilePicker') @Watch('onFilePickerEvent') geckoFilePicker: string = '';
  @StorageProp('geckoFullscreen') @Watch('onFullscreenChanged') geckoFullscreen: boolean = false;
  @State private downloadText: string = '';
  @State private downloadVisible: boolean = false;
  @State private zoomLevel: number = 1.0;
  @State private findVisible: boolean = false;
  @State private findQuery: string = '';
  @State private findMatchCase: boolean = false;
  @State private fullscreenUi: boolean = false;
  @StorageProp('geckoMenuSeq') @Watch('onMenuEvent') geckoMenuSeq: number = 0;
  @StorageProp('geckoMenu') geckoMenuRaw: string = '';
  @State private menuVisible: boolean = false;
  @State private menuId: number = 0;
  @State private menuRows: Array<MenuRow> = [];
  @State private menuX: number = 0;
  @State private menuY: number = 0;
  @State private contentWidth: number = 0;
  @State private suggestions: Array<string> = [];
  @State private showSuggestions: boolean = false;
  private lastHistoryUrl: string = '';
  @State private contentHeight: number = 0;
  private menuTree: Array<MenuItem> = new Array<MenuItem>();
  private expandedMenuIds: Array<number> = new Array<number>();
  private downloadHideTimer: number = -1;
  // Per-tab URL stacks used for back/forward (the port's session-history NAPI
  // is not available at runtime, so the shell tracks navigation itself).
  private tabHistory: Map<string, Array<string>> = new Map();
  private tabHistoryIndex: Map<string, number> = new Map();
  private suppressHistoryPush: boolean = false;
  // ArkTS tabId <-> engine browserIndex (the port's sessionId). Engine browser 0
  // is created by geckoview.js at startup; new tabs start at 1.
  private engineIndexByTab: Map<string, number> = new Map();
  private tabByEngineIndex: Map<number, string> = new Map();
  private nextEngineIndex: number = 1;
  @StorageProp('engineUnclean') engineUnclean: boolean = false;
  @StorageProp('skipResume') skipResume: boolean = false;
  @StorageProp('debugCtxMenu') debugCtxMenu: boolean = false;
  @State private showRecoveryBanner: boolean = false;
  @State private recoveredCount: number = 0;
  @State private recoveredLastUrl: string = '';
  @State private loadError: string = '';
  private loadWatchdog: number = -1;
  private loadSettled: boolean = true;
  private saveTimer: number = -1;
  private store: SessionStore = SessionStore.instance();
  @State private currentTitle: string = '新标签页';
  @State private loading: boolean = false;
  @State private privateMode: boolean = false;
  @State private activePanel: string = PANEL_NONE;

  @State private bookmarks: Array<Bookmark> = [];
  @State private historyEntries: Array<HistoryEntry> = [];
  @State private downloadRecords: Array<DownloadRecord> = [];

  @State private javascriptEnabled: boolean = true;
  @State private imagesEnabled: boolean = true;
  @State private doNotTrack: boolean = true;
  @State private privateByDefault: boolean = false;
  @State private searchEngine: string = 'DuckDuckGo';

  @State private accountName: string = '';
  @State private engineLabel: string = '正在初始化原生桥…';
  @State private statusMessage: string = '';
  @State private engineRenderReady: boolean = false;

  private viewModel: TabViewModel = new TabViewModel();
  private settings: SettingsRepository = new SettingsRepository();
  private database: BrowserDatabase = new BrowserDatabase();
  private accountService: LocalAccountService = new LocalAccountService();
  private gecko: GeckoService = GeckoService.getInstance();
  private contextRef: common.UIAbilityContext | undefined = undefined;

  aboutToAppear(): void {
    this.viewModel.onChange = () => {
      this.syncTabs();
    };
    this.bootstrap();
  }

  aboutToDisappear(): void {
    this.gecko.release();
  }

  // -------------------- P1: downloads / picker / fullscreen / find / zoom ----
  private onDownloadEvent(): void {
    if (this.geckoDownload.length === 0) {
      return;
    }
    try {
      const event: DownloadEvent = JSON.parse(this.geckoDownload) as DownloadEvent;
      let text: string = '';
      if (event.type === 'start') {
        text = `开始下载：${event.filename !== undefined ? event.filename : event.url}`;
      } else if (event.type === 'progress') {
        const total: number = event.totalBytes !== undefined ? event.totalBytes : 0;
        const got: number = event.receivedBytes !== undefined ? event.receivedBytes : 0;
        const pct: number = total > 0 ? Math.round(got * 100 / total) : 0;
        text = `下载中：${pct}%`;
      } else if (event.type === 'complete') {
        text = `下载完成：${event.path}`;
        this.recordDownload(event, DownloadState.COMPLETED);
      } else if (event.type === 'failed') {
        text = `下载失败：${event.errorCode}`;
        this.recordDownload(event, DownloadState.FAILED);
      } else {
        return;
      }
      hilog.info(DOMAIN, TAG, 'download event: %{public}s', text);
      this.downloadText = text;
      this.downloadVisible = true;
      if (this.downloadHideTimer >= 0) {
        clearTimeout(this.downloadHideTimer);
      }
      if (event.type === 'complete' || event.type === 'failed') {
        this.downloadHideTimer = setTimeout(() => {
          this.downloadVisible = false;
        }, 5000);
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'download event parse failed: %{public}s', JSON.stringify(error));
    }
  }

  private recordDownload(event: DownloadEvent, state: DownloadState): void {
    try {
      const record = new DownloadRecord();
      record.id = `dl_${event.id}_${Date.now()}`;
      record.profileId = PROFILE_ID;
      record.url = event.url !== undefined ? event.url : '';
      record.fileName = event.filename !== undefined ? event.filename : '';
      record.totalBytes = event.totalBytes !== undefined ? event.totalBytes : 0;
      record.receivedBytes = event.receivedBytes !== undefined ? event.receivedBytes : record.totalBytes;
      record.state = state;
      record.localPath = event.path !== undefined ? event.path : '';
      record.createdAt = Date.now();
      this.database.upsertDownload(record).then(() => {
        this.refreshPanels();
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'download record failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'recordDownload failed: %{public}s', JSON.stringify(error));
    }
  }

  private onFilePickerEvent(): void {
    if (this.geckoFilePicker.length === 0) {
      return;
    }
    try {
      hilog.info(DOMAIN, TAG, 'file picker request: %{public}s', this.geckoFilePicker);
      const wrapper: PickerEvent = JSON.parse(this.geckoFilePicker) as PickerEvent;
      const req: PickerRequest = JSON.parse(wrapper.req) as PickerRequest;
      this.openFilePicker(wrapper.id, req);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'file picker parse failed: %{public}s', JSON.stringify(error));
    }
  }

  private async openFilePicker(callbackId: number, req: PickerRequest): Promise<void> {
    if (this.contextRef === undefined) {
      GeckoViewBoot.resolveFilePicker(callbackId, 1, '');
      return;
    }
    try {
      hilog.info(DOMAIN, TAG, 'opening system picker mode=%{public}s', req.mode);
      const documentPicker = new picker.DocumentViewPicker(this.contextRef);
      const options = new picker.DocumentSelectOptions();
      options.maxSelectNumber = req.mode === 'multiple' ? 10 : 1;
      if (req.suffixes !== undefined && req.suffixes.length > 0) {
        options.fileSuffixFilters = req.suffixes;
      }
      const uris: Array<string> = await documentPicker.select(options);
      hilog.info(DOMAIN, TAG, 'picker returned %{public}d uris', uris === undefined ? 0 : uris.length);
      if (uris === undefined || uris.length === 0) {
        GeckoViewBoot.resolveFilePicker(callbackId, 1, '');
        return;
      }
      const paths: Array<string> = new Array<string>();
      for (let i = 0; i < uris.length; i++) {
        // Picker grants a file://docs/... URI; copy it into the sandbox so
        // Gecko can InitWithNativePath on a real absolute path.
        const srcFd = p1fs.openSync(uris[i], p1fs.OpenMode.READ_ONLY);
        const base: string = uris[i].substring(uris[i].lastIndexOf('/') + 1);
        const dst: string = `${this.contextRef.cacheDir}/picked_${Date.now()}_${i}_${base}`;
        p1fs.copyFileSync(srcFd.fd, dst);
        p1fs.closeSync(srcFd);
        paths.push(dst);
      }
      if (req.mode === 'multiple') {
        GeckoViewBoot.resolveFilePicker(callbackId, 0, JSON.stringify(paths));
      } else {
        GeckoViewBoot.resolveFilePicker(callbackId, 0, paths[0]);
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'openFilePicker failed/cancelled: %{public}s', JSON.stringify(error));
      GeckoViewBoot.resolveFilePicker(callbackId, 1, '');
    }
  }

  private onFullscreenChanged(): void {
    this.fullscreenUi = this.geckoFullscreen;
    if (this.contextRef === undefined) {
      return;
    }
    try {
      p1window.getLastWindow(this.contextRef).then((win: p1window.Window) => {
        win.setWindowLayoutFullScreen(this.geckoFullscreen);
        win.setWindowSystemBarEnable(this.geckoFullscreen ? [] : ['status', 'navigation']);
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'fullscreen apply failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'fullscreen failed: %{public}s', JSON.stringify(error));
    }
  }

  private onMenuEvent(): void {
    if (this.geckoMenuRaw.length === 0) {
      return;
    }
    try {
      const payload: MenuPayload = JSON.parse(this.geckoMenuRaw) as MenuPayload;
      if (payload === undefined || payload.items === undefined || payload.items.length === 0) {
        return;
      }
      this.menuTree = payload.items;
      this.expandedMenuIds = new Array<number>();
      this.rebuildMenuRows();
      if (this.menuRows.length === 0) {
        return;
      }
      this.menuId = payload.menuId;
      const ax: number = payload.anchor !== undefined ? payload.anchor.x : 0;
      const ay: number = payload.anchor !== undefined ? payload.anchor.y : 0;
      const ah: number = payload.anchor !== undefined ? payload.anchor.h : 0;
      // Port delivers anchor in device px (CSS px * 3 in this chrome doc);
      // ArkUI positions are vp, and CSS px ~= vp here, so divide by 3.
      let x: number = Math.max(8, Math.floor(ax / 3));
      let y: number = Math.max(8, Math.floor((ay + ah) / 3));
      const menuWidth: number = 260;
      const menuHeight: number = Math.min(420, this.menuRows.length * 36 + 12);
      if (this.contentWidth > 0 && x + menuWidth > this.contentWidth - 8) {
        x = Math.max(8, this.contentWidth - menuWidth - 8);
      }
      if (this.contentHeight > 0 && y + menuHeight > this.contentHeight - 8) {
        y = Math.max(8, y - menuHeight - 8);
      }
      this.menuX = x;
      this.menuY = y;
      this.menuVisible = true;
      hilog.info(DOMAIN, TAG, 'menu shown id=%{public}d rows=%{public}d', this.menuId, this.menuRows.length);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'menu parse failed: %{public}s', JSON.stringify(error));
    }
  }

  private flattenMenu(items: Array<MenuItem>, depth: number, out: Array<MenuRow>): void {
    for (let i = 0; i < items.length; i++) {
      const item: MenuItem = items[i];
      if (item.hidden) {
        continue;
      }
      const row = new MenuRow();
      row.kind = item.kind;
      row.id = item.id;
      row.label = item.label;
      row.accel = item.accel;
      row.disabled = item.disabled;
      row.checked = item.checked;
      row.depth = depth;
      row.hasChildren = item.items !== undefined && item.items.length > 0;
      row.expanded = this.expandedMenuIds.indexOf(item.id) >= 0;
      out.push(row);
      if (row.hasChildren && row.expanded && depth < 3) {
        this.flattenMenu(item.items as Array<MenuItem>, depth + 1, out);
      }
    }
  }

  private rebuildMenuRows(): void {
    const rows: Array<MenuRow> = new Array<MenuRow>();
    this.flattenMenu(this.menuTree, 0, rows);
    this.menuRows = rows;
  }

  /** Expands/collapses a submenu row (port renders submenus flat). */
  private toggleMenuRow(row: MenuRow): void {
    const index: number = this.expandedMenuIds.indexOf(row.id);
    if (index >= 0) {
      this.expandedMenuIds.splice(index, 1);
    } else {
      this.expandedMenuIds.push(row.id);
    }
    this.rebuildMenuRows();
  }

  private tapMenuRow(row: MenuRow): void {
    if (row.disabled || row.kind === 'separator' || row.id === 0) {
      return;
    }
    if (row.hasChildren) {
      this.toggleMenuRow(row);
      return;
    }
    GeckoViewBoot.resolveMenuCommand(this.menuId, row.id, 0);
    this.menuVisible = false;
  }

  private closeMenu(sendToGecko: boolean): void {
    if (sendToGecko) {
      GeckoViewBoot.closeNativeMenu(this.menuId);
    }
    this.menuVisible = false;
  }

  private zoomBy(delta: number): void {
    this.zoomLevel = Math.min(3.0, Math.max(0.5, this.zoomLevel + delta));
    GeckoViewBoot.setFullZoom(this.zoomLevel);
  }

  private findNext(backward: boolean): void {
    if (this.findQuery.length === 0) {
      return;
    }
    GeckoViewBoot.findInPage(this.findQuery, backward, this.findMatchCase);
  }

  private async bootstrap(): Promise<void> {
    const context = getContext(this) as common.UIAbilityContext;
    this.contextRef = context;

    try {
      await this.database.init(context);
    } catch (error) {
      this.statusMessage = `数据库初始化失败：${JSON.stringify(error)}`;
      hilog.error(DOMAIN, TAG, 'database init failed');
    }

    try {
      this.settings.init(context);
      this.javascriptEnabled = this.settings.isJavascriptEnabled();
      this.imagesEnabled = this.settings.areImagesEnabled();
      this.doNotTrack = this.settings.isDoNotTrackEnabled();
      this.privateByDefault = this.settings.isPrivateByDefault();
      this.searchEngine = this.settings.getSearchEngine();
    } catch (error) {
      this.statusMessage = `设置读取失败：${JSON.stringify(error)}`;
    }

    try {
      this.accountService.init(context);
      const account = this.accountService.getAccount();
      if (account !== undefined) {
        this.accountName = account.displayName;
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'account store unavailable');
    }

    const bridgeReady: boolean = await this.gecko.initialize();
    const version = this.gecko.getVersionSummary();
    if (bridgeReady) {
      this.engineLabel = `${version.engine} ${version.buildId} · ${version.abi} · js=${version.jsEngine} · 可用性=${version.availability}`;
      this.engineRenderReady = bridgeReady || version.availability === EngineAvailability.READY;
    } else {
      this.engineLabel = '原生桥不可用（HSP/NAPI 未加载）';
      this.engineRenderReady = false;
    }

    this.viewModel.configure(PROFILE_ID, this.privateByDefault);
    this.privateMode = this.privateByDefault;
    const saved: SavedSession | undefined = this.skipResume ? undefined : this.store.load();
    if (saved !== undefined && saved.tabs.length > 0) {
      this.restoreSession(saved);
      if (this.engineUnclean) {
        this.recoveredCount = saved.tabs.length;
        const lastIdx: number = Math.min(Math.max(saved.activeIndex, 0), saved.tabs.length - 1);
        this.recoveredLastUrl = saved.tabs[lastIdx].url;
        this.showRecoveryBanner = true;
        setTimeout(() => {
          this.showRecoveryBanner = false;
        }, 8000);
        hilog.warn(DOMAIN, TAG, 'unclean exit detected, restored %{public}d tabs, last=%{public}s',
          saved.tabs.length, this.recoveredLastUrl);
      } else {
        hilog.info(DOMAIN, TAG, 'session restored (%{public}d tabs)', saved.tabs.length);
      }
    } else {
      const firstTab = this.viewModel.createTab(TabViewModel.homeUrl());
      // Engine browser 0 is created by geckoview.js at startup with the same URL.
      this.bindEngineSession(firstTab.id, 0);
      this.pushHistory(firstTab.id, 'https://example.com/');
      this.viewModel.navigate(firstTab.id, 'https://example.com/');
      this.viewModel.markLoaded(firstTab.id, 'Example Domain');
    }
    if (this.engineRenderReady) {
      this.startLoadWatchdog();
    }
    if (this.debugCtxMenu) {
      setTimeout(() => {
        const size = GeckoViewBoot.surfaceSize();
        const cx: number = Math.round(size.width / 2);
        const cy: number = Math.round(size.height / 2);
        hilog.info(DOMAIN, TAG, 'ctxmenu probe at %{public}d,%{public}d', cx, cy);
        GeckoViewBoot.mouseDown(cx, cy, 2);
        setTimeout(() => {
          GeckoViewBoot.mouseUp(cx, cy, 2);
        }, 80);
      }, 4000);
    }
    await this.refreshPanels();
  }

  private bindEngineSession(tabId: string, engineIndex: number): void {
    this.engineIndexByTab.set(tabId, engineIndex);
    this.tabByEngineIndex.set(engineIndex, tabId);
  }

  private engineIndexOfTab(tabId: string): number | undefined {
    return this.engineIndexByTab.get(tabId);
  }

  private activeEngineIndex(): number | undefined {
    return this.engineIndexOfTab(this.viewModel.getActiveTabId());
  }

  /** Force a repaint after docShellIsActive switch (port needs the toggle). */
  private repaintSoon(): void {
    setTimeout(() => {
      GeckoViewBoot.forceRepaint();
    }, 150);
  }

  /** Engine URL change keeps the address bar and the active tab's URL in sync. */
  private onGeckoUrlChanged(): void {
    if (this.geckoUrl.length === 0) {
      return;
    }
    this.currentUrl = this.geckoUrl;
    this.stopLoadWatchdog();
    const activeTabId: string = this.viewModel.getActiveTabId();
    if (activeTabId.length > 0) {
      this.viewModel.setUrl(activeTabId, this.geckoUrl);
    }
    hilog.info(DOMAIN, TAG, 'engine url -> %{public}s (session=%{public}s)', this.geckoUrl, this.geckoSession);
    setTimeout(() => {
      this.refreshHistoryState();
    }, 600);
  }

  /** Real page title from the engine keeps the tab chip and header in sync. */
  private onGeckoTitleChanged(): void {
    if (this.geckoTitleEvent.length === 0) {
      return;
    }
    try {
      const event: TitleEvent = JSON.parse(this.geckoTitleEvent) as TitleEvent;
      if (event.session === '__opentab__') {
        this.openUrlInNewTab(event.url);
        return;
      }
      if (event.title.length === 0) {
        return;
      }
      this.currentTitle = event.title;
    this.stopLoadWatchdog();
      // Resolve the tab that owns this engine session, falling back to active.
      let tabId: string = this.viewModel.getActiveTabId();
      const engineIndex: number = Number(event.session);
      if (!Number.isNaN(engineIndex)) {
        const mapped: string | undefined = this.tabByEngineIndex.get(engineIndex);
        if (mapped !== undefined) {
          tabId = mapped;
        }
      }
      if (tabId.length > 0) {
        this.viewModel.markLoaded(tabId, event.title);
        hilog.info(DOMAIN, TAG, 'title applied tab=%{public}s title=%{public}s seq=%{public}d',
          tabId, event.title, event.seq);
        this.syncTabs();
      }
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'title event parse failed: %{public}s', JSON.stringify(error));
    }
  }

  /** Creates a tab + engine session for a URL requested by the chrome menu. */
  private openUrlInNewTab(url: string): void {
    if (url.length === 0) {
      return;
    }
    const created = this.viewModel.createTab(url);
    const engineIndex: number = this.nextEngineIndex++;
    this.bindEngineSession(created.id, engineIndex);
    this.viewModel.activateTab(created.id);
    GeckoViewBoot.createSession(engineIndex, url);
    GeckoViewBoot.switchToSession(engineIndex);
    this.viewModel.navigate(created.id, url);
    this.pushHistory(created.id, url);
    this.startLoadWatchdog();
    this.repaintSoon();
    this.syncTabs();
    hilog.info(DOMAIN, TAG, 'openUrlInNewTab %{public}s idx=%{public}d', url, engineIndex);
  }

  /** Records the active engine URL into history once per navigation. */
  private recordEngineHistory(): void {
    if (this.privateMode) {
      return;
    }
    const url: string = this.currentUrl;
    if (!url.startsWith('http') || url === this.lastHistoryUrl) {
      return;
    }
    this.lastHistoryUrl = url;
    try {
      const entry = HistoryEntry.create(PROFILE_ID, url, this.currentTitle);
      this.database.addHistory(entry).then(() => {
        this.refreshPanels();
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'engine history write failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'engine history create failed');
    }
  }

  private onAddressInput(text: string): void {
    if (text.length === 0) {
      this.showSuggestions = false;
      return;
    }
    const query: string = text.toLowerCase();
    const seen: Array<string> = new Array<string>();
    const hits: Array<string> = new Array<string>();
    const add = (value: string): void => {
      if (value.length === 0 || value === text || seen.indexOf(value) >= 0) {
        return;
      }
      const lower: string = value.toLowerCase();
      if (lower.indexOf(query) < 0 && lower.indexOf('http') !== 0) {
        return;
      }
      if (lower.indexOf(query) < 0) {
        return;
      }
      seen.push(value);
      hits.push(value);
    };
    for (let i = 0; i < this.bookmarks.length && hits.length < 8; i++) {
      add(this.bookmarks[i].url);
    }
    for (let i = 0; i < this.historyEntries.length && hits.length < 8; i++) {
      add(this.historyEntries[i].url);
    }
    this.suggestions = hits;
    this.showSuggestions = hits.length > 0;
  }

  private pickSuggestion(url: string): void {
    this.showSuggestions = false;
    this.navigate(url);
  }

  private onGeckoPageLoadChanged(): void {
    this.loading = this.geckoPageLoad === 'start';
    if (this.loading) {
      this.loadError = '';
      this.startLoadWatchdog();
    } else {
      this.stopLoadWatchdog();
      this.refreshHistoryState();
      this.recordEngineHistory();
    }
  }

  /** Mirrors the active engine session's history position into the UI. */
  /** Recomputed canGoBack/canGoForward from the ArkTS-side history stacks. */
  private refreshHistoryState(): void {
    const tabId: string = this.viewModel.getActiveTabId();
    const urls: Array<string> | undefined = this.tabHistory.get(tabId);
    const index: number = this.tabHistoryIndex.get(tabId) ?? 0;
    const count: number = urls !== undefined ? urls.length : 0;
    this.canGoBack = count > 0 && index > 0;
    this.canGoForward = count > 0 && index + 1 < count;
    hilog.info(DOMAIN, TAG, 'history index=%{public}d count=%{public}d back=%{public}s fwd=%{public}s',
      index, count, `${this.canGoBack}`, `${this.canGoForward}`);
  }

  /** Records a committed navigation for the tab (dedupes consecutive URLs). */
  private pushHistory(tabId: string, url: string): void {
    if (url.length === 0 || this.suppressHistoryPush) {
      return;
    }
    let urls: Array<string> | undefined = this.tabHistory.get(tabId);
    if (urls === undefined) {
      urls = new Array<string>();
      this.tabHistory.set(tabId, urls);
    }
    let index: number = this.tabHistoryIndex.get(tabId) ?? -1;
    if (index >= 0 && index < urls.length && urls[index] === url) {
      return;
    }
    while (urls.length > index + 1) {
      urls.pop();
    }
    urls.push(url);
    this.tabHistoryIndex.set(tabId, urls.length - 1);
    this.refreshHistoryState();
  }

  /** Loads a history entry and updates the cursor without re-pushing it. */
  private loadHistoryEntry(tabId: string, entryIndex: number): void {
    const urls: Array<string> | undefined = this.tabHistory.get(tabId);
    if (urls === undefined || entryIndex < 0 || entryIndex >= urls.length) {
      return;
    }
    const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
    if (engineIndex === undefined) {
      return;
    }
    this.suppressHistoryPush = true;
    this.tabHistoryIndex.set(tabId, entryIndex);
    const url: string = urls[entryIndex];
    try {
      GeckoViewBoot.loadUrlForSession(engineIndex, url);
      this.repaintSoon();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'history load failed: %{public}s', JSON.stringify(error));
    }
    setTimeout(() => {
      this.suppressHistoryPush = false;
      this.refreshHistoryState();
    }, 900);
    this.refreshHistoryState();
  }
  private back(): void {
    const tabId: string = this.viewModel.getActiveTabId();
    const index: number = this.tabHistoryIndex.get(tabId) ?? 0;
    if (index <= 0) {
      return;
    }
    this.loadHistoryEntry(tabId, index - 1);
    this.syncTabs();
  }

  private forward(): void {
    const tabId: string = this.viewModel.getActiveTabId();
    const urls: Array<string> | undefined = this.tabHistory.get(tabId);
    const index: number = this.tabHistoryIndex.get(tabId) ?? 0;
    if (urls === undefined || index + 1 >= urls.length) {
      return;
    }
    this.loadHistoryEntry(tabId, index + 1);
    this.syncTabs();
  }

  private reload(): void {
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex === undefined) {
      return;
    }
    try {
      GeckoViewBoot.reloadForSession(engineIndex);
      this.repaintSoon();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'reload failed: %{public}s', JSON.stringify(error));
    }
  }

  private stopLoading(): void {
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex !== undefined) {
      try {
        GeckoViewBoot.stopForSession(engineIndex);
      } catch (error) {
        hilog.warn(DOMAIN, TAG, 'stop failed: %{public}s', JSON.stringify(error));
      }
    }
    this.viewModel.markStopped(this.activeTabId);
  }

  private dismissKeyboard(): void {
    try {
      this.getUIContext().getFocusController().clearFocus();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'clearFocus failed: %{public}s', JSON.stringify(error));
    }
  }

  private syncTabs(): void {
    const chips: Array<TabChip> = [];
    const models = this.viewModel.snapshot();
    for (let index = 0; index < models.length; index++) {
      const model = models[index];
      chips.push(TabChip.of(model.id, model.title, model.url, model.isPrivate));
    }
    this.tabs = chips;
    this.activeTabId = this.viewModel.getActiveTabId();

    const active = this.viewModel.getActiveTab();
    if (active !== undefined) {
      this.currentUrl = active.url;
      this.currentTitle = active.title.length > 0 ? active.title : active.url;
      this.loading = active.loadingState === LoadingState.LOADING;
    } else {
      this.currentUrl = '';
      this.currentTitle = '新标签页';
      this.loading = false;
    }
    this.scheduleSessionSave();
  }

  /** Recreates ArkTS tabs and engine sessions from a persisted snapshot. */
  private restoreSession(saved: SavedSession): void {
    const restoredIds: Array<string> = [];
    for (let i = 0; i < saved.tabs.length; i++) {
      const tab = saved.tabs[i];
      const created = this.viewModel.createTab(tab.url.length > 0 ? tab.url : TabViewModel.homeUrl());
      const engineIndex: number = i === 0 ? 0 : this.nextEngineIndex++;
      this.bindEngineSession(created.id, engineIndex);
      this.pushHistory(created.id, tab.url);
      this.viewModel.markLoaded(created.id, tab.title);
      restoredIds.push(created.id);
      if (engineIndex > 0) {
        GeckoViewBoot.createSession(engineIndex, tab.url);
      }
    }
    const activeIndex: number = Math.min(Math.max(saved.activeIndex, 0), restoredIds.length - 1);
    this.viewModel.activateTab(restoredIds[activeIndex]);
    if (activeIndex > 0) {
      GeckoViewBoot.switchToSession(activeIndex);
    } else {
      GeckoViewBoot.loadUrlForSession(0, saved.tabs[0].url);
    }
    GeckoViewBoot.forceRepaint();
    this.syncTabs();
  }

  private scheduleSessionSave(): void {
    if (this.saveTimer >= 0) {
      clearTimeout(this.saveTimer);
    }
    this.saveTimer = setTimeout(() => {
      this.persistSession();
    }, 400);
  }

  private persistSession(): void {
    try {
      const models = this.viewModel.snapshot();
      if (models.length === 0) {
        return;
      }
      const session = new SavedSession();
      session.tabs = new Array<SavedTab>();
      let activeIndex: number = 0;
      const activeId: string = this.viewModel.getActiveTabId();
      for (let i = 0; i < models.length; i++) {
        const tab = new SavedTab();
        tab.url = models[i].url;
        tab.title = models[i].title;
        session.tabs.push(tab);
        if (models[i].id === activeId) {
          activeIndex = i;
        }
      }
      session.activeIndex = activeIndex;
      this.store.save(session);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'persistSession failed: %{public}s', JSON.stringify(error));
    }
  }

  private startLoadWatchdog(): void {
    this.stopLoadWatchdog();
    this.loadSettled = false;
    this.loading = true;
    this.loadWatchdog = setTimeout(() => {
      if (!this.loadSettled) {
        this.loadError = '页面加载超时：请检查网络连接，或重试。';
        this.loading = false;
        hilog.warn(DOMAIN, TAG, 'load watchdog fired');
      }
    }, 20000);
  }

  private stopLoadWatchdog(): void {
    this.loadSettled = true;
    if (this.loadWatchdog >= 0) {
      clearTimeout(this.loadWatchdog);
      this.loadWatchdog = -1;
    }
  }

  private retryLoad(): void {
    this.loadError = '';
    const engineIndex: number | undefined = this.activeEngineIndex();
    if (engineIndex !== undefined) {
      GeckoViewBoot.reloadForSession(engineIndex);
      this.repaintSoon();
      this.startLoadWatchdog();
    }
  }

  private goHome(): void {
    this.loadError = '';
    this.navigate('https://example.com/');
  }

  private async refreshPanels(): Promise<void> {
    if (this.privateMode) {
      this.bookmarks = [];
      this.historyEntries = [];
      this.downloadRecords = [];
      return;
    }
    try {
      this.bookmarks = await this.database.listBookmarks(PROFILE_ID);
      this.historyEntries = await this.database.listHistory(PROFILE_ID, 100);
      this.downloadRecords = await this.database.listDownloads(PROFILE_ID);
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'panel refresh failed: %{public}s', JSON.stringify(error));
    }
  }

  private async navigate(input: string): Promise<void> {
    const resolved: string = TabViewModel.normalizeInput(input, this.searchEngine);
    let tabId: string = this.viewModel.getActiveTabId();
    if (tabId.length === 0) {
      const created = this.viewModel.createTab(resolved);
      tabId = created.id;
      const engineIndex: number = this.nextEngineIndex++;
      this.bindEngineSession(tabId, engineIndex);
      if (this.engineRenderReady) {
        GeckoViewBoot.createSession(engineIndex, resolved);
        GeckoViewBoot.switchToSession(engineIndex);
        this.repaintSoon();
      }
    } else {
      this.viewModel.navigate(tabId, resolved);
    }

    const title: string = this.titleForUrl(resolved);
    if (this.engineRenderReady) {
      try {
        const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
        if (engineIndex !== undefined) {
          GeckoViewBoot.loadUrlForSession(engineIndex, resolved);
        } else {
          GeckoViewBoot.loadUrl(resolved);
        }
        this.pushHistory(tabId, resolved);
        this.startLoadWatchdog();
      } catch (error) {
        const geckoError: GeckoError = toGeckoError(error as Object);
        this.statusMessage = `loadUrl failed: ${geckoError.code}`;
      }
    } else {
      this.statusMessage = 'Gecko engine not embedded yet (M2/M3).';
    }

    this.viewModel.markLoaded(tabId, title);

    if (!this.privateMode && resolved.startsWith('http')) {
      try {
        const entry = HistoryEntry.create(PROFILE_ID, resolved, title);
        await this.database.addHistory(entry);
        this.lastHistoryUrl = resolved;
        await this.refreshPanels();
      } catch (error) {
        hilog.warn(DOMAIN, TAG, 'history write failed');
      }
    }
    this.syncTabs();
  }

  private titleForUrl(url: string): string {
    if (url === TabViewModel.homeUrl()) {
      return '主页';
    }
    if (url.startsWith('about:search')) {
      return '搜索（引擎待接入）';
    }
    return url;
  }

  private async addCurrentBookmark(): Promise<void> {
    if (this.privateMode) {
      this.statusMessage = '隐私模式不保存书签。';
      return;
    }
    const active = this.viewModel.getActiveTab();
    if (active === undefined || active.url.length === 0) {
      this.statusMessage = '当前标签页没有可收藏的地址。';
      return;
    }
    try {
      const bookmark = Bookmark.create(PROFILE_ID, active.url, this.currentTitle);
      await this.database.addBookmark(bookmark);
      await this.refreshPanels();
      this.statusMessage = `已收藏：${this.currentTitle}`;
    } catch (error) {
      this.statusMessage = '收藏失败。';
    }
  }

  private async removeBookmark(id: string): Promise<void> {
    try {
      await this.database.removeBookmark(id);
      await this.refreshPanels();
    } catch (error) {
      this.statusMessage = '删除书签失败。';
    }
  }

  private async clearHistory(): Promise<void> {
    try {
      await this.database.clearHistory(PROFILE_ID);
      await this.refreshPanels();
      this.statusMessage = '历史已清空。';
    } catch (error) {
      this.statusMessage = '清空历史失败。';
    }
  }

  private openDownload(id: string): void {
    if (this.contextRef === undefined) {
      return;
    }
    let path: string = '';
    for (const record of this.downloadRecords) {
      if (record.id === id) {
        path = record.localPath;
        break;
      }
    }
    if (path.length === 0) {
      return;
    }
    try {
      const uri: string = fileUri.getUriFromPath(path);
      let mime: string = '*/*';
      const lower: string = path.toLowerCase();
      if (lower.endsWith('.svg')) {
        mime = 'image/svg+xml';
      } else if (lower.endsWith('.png')) {
        mime = 'image/png';
      } else if (lower.endsWith('.jpg') || lower.endsWith('.jpeg')) {
        mime = 'image/jpeg';
      } else if (lower.endsWith('.txt')) {
        mime = 'text/plain';
      } else if (lower.endsWith('.pdf')) {
        mime = 'application/pdf';
      }
      this.contextRef.startAbility({
        action: 'ohos.want.action.viewData',
        uri: uri,
        type: mime
      }).catch((error: Object) => {
        hilog.warn(DOMAIN, TAG, 'open download failed');
      });
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'open download error');
    }
  }

  private clearDownloads(): void {
    const records: Array<DownloadRecord> = this.downloadRecords;
    for (let i = 0; i < records.length; i++) {
      const path: string = records[i].localPath;
      if (path.length > 0) {
        try {
          p1fs.unlinkSync(path);
        } catch (error) {
        }
      }
    }
    this.database.clearDownloads(PROFILE_ID).then(() => {
      this.refreshPanels();
    }).catch((error: Object) => {
      hilog.warn(DOMAIN, TAG, 'clear downloads failed');
    });
  }

  private async cancelDownload(id: string): Promise<void> {
    for (let index = 0; index < this.downloadRecords.length; index++) {
      const record = this.downloadRecords[index];
      if (record.id === id) {
        record.state = DownloadState.CANCELED;
        try {
          await this.database.upsertDownload(record);
        } catch (error) {
          hilog.warn(DOMAIN, TAG, 'download update failed');
        }
      }
    }
    await this.refreshPanels();
  }

  private async retryDownload(id: string): Promise<void> {
    for (let index = 0; index < this.downloadRecords.length; index++) {
      const record = this.downloadRecords[index];
      if (record.id === id) {
        record.state = DownloadState.QUEUED;
        try {
          await this.database.upsertDownload(record);
        } catch (error) {
          hilog.warn(DOMAIN, TAG, 'download update failed');
        }
      }
    }
    await this.refreshPanels();
  }

  private togglePrivateMode(): void {
    this.privateMode = !this.privateMode;
    this.viewModel.setPrivateMode(this.privateMode);
    this.refreshPanels();
    this.statusMessage = this.privateMode ? '已进入隐私模式：不写历史与书签，退出时清理会话。' : '已退出隐私模式。';
  }

  private openPanel(panel: string): void {
    this.activePanel = this.activePanel === panel ? PANEL_NONE : panel;
  }

  private openDiagnostics(): void {
    const options: router.RouterOptions = { url: 'pages/Index' };
    try {
      this.getUIContext().getRouter().pushUrl(options);
    } catch (error) {
      this.statusMessage = '无法打开诊断页。';
    }
  }

  private async exportData(): Promise<void> {
    const context = this.contextRef;
    if (context === undefined) {
      return;
    }
    try {
      const payload = await this.accountService.buildExport(this.database, this.settings, PROFILE_ID);
      const uri = await this.accountService.exportToFile(context, payload);
      this.statusMessage = uri.length > 0 ? `已导出到 ${uri}` : '已取消导出。';
    } catch (error) {
      this.statusMessage = '导出失败。';
    }
  }

  private async importData(): Promise<void> {
    const context = this.contextRef;
    if (context === undefined) {
      return;
    }
    try {
      const count = await this.accountService.importFromFile(context, this.database, PROFILE_ID);
      await this.refreshPanels();
      this.statusMessage = count > 0 ? `已导入 ${count} 条记录。` : '已取消导入。';
    } catch (error) {
      this.statusMessage = '导入失败：文件格式不正确。';
    }
  }

  @Builder
  panelButton(label: string, panel: string) {
    Button(label)
      .fontSize(11)
      .height(26)
      .backgroundColor(this.activePanel === panel ? '#2A3550' : '#17171F')
      .fontColor(this.activePanel === panel ? '#CFE0FF' : '#A0A0B8')
      .borderRadius(6)
      .onClick(() => {
        this.openPanel(panel);
      })
  }

  @Builder
  placeholderContent() {
    Column({ space: 10 }) {
      Text(this.currentTitle)
        .fontSize(20)
        .fontWeight(FontWeight.Medium)
        .fontColor('#F2F2FA')
        .maxLines(2)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
      Text(this.currentUrl.length > 0 ? this.currentUrl : 'about:newtab')
        .fontSize(13)
        .fontColor('#8A8AA3')
        .maxLines(2)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
      Text('Gecko 渲染未启用：XComponent(SURFACE) 已就绪，内容渲染按 M3 门禁推进。')
        .fontSize(12)
        .fontColor('#7C7C96')
        .textAlign(TextAlign.Center)
      if (this.privateMode) {
        Text('隐私模式：历史与书签不写入，退出后会话清理。')
          .fontSize(12)
          .fontColor('#C9A7FF')
          .textAlign(TextAlign.Center)
      }
    }
    .width('100%')
    .height('100%')
    .padding(24)
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
    .backgroundColor('#0E0E12')
  }

  build() {
    Column() {
      if (this.showRecoveryBanner) {
        Row({ space: 8 }) {
          Text(`检测到上次异常退出，已自动恢复 ${this.recoveredCount} 个标签${this.recoveredLastUrl.length > 0 ? '（上次停留：' + (this.recoveredLastUrl.length > 40 ? this.recoveredLastUrl.substring(0, 40) + '…' : this.recoveredLastUrl) + '）' : ''}`)
            .fontSize(12)
            .fontColor('#F2D9A0')
            .layoutWeight(1)
          Button('知道了')
            .fontSize(12)
            .height(28)
            .backgroundColor('#3A3220')
            .fontColor('#F2D9A0')
            .onClick(() => {
              this.showRecoveryBanner = false;
            })
        }
        .width('100%')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#2A2418')
      }

      if (!this.fullscreenUi) {
      AddressBar({
        url: this.currentUrl,
        canGoBack: this.canGoBack,
        canGoForward: this.canGoForward,
        loading: this.loading,
        privateMode: this.privateMode,
        onNavigate: (input: string) => {
          this.showSuggestions = false;
          this.navigate(input);
        },
        onInput: (text: string) => {
          this.onAddressInput(text);
        },
        onBack: () => {
          this.back();
        },
        onForward: () => {
          this.forward();
        },
        onReload: () => {
          this.reload();
        },
        onStop: () => {
          this.stopLoading();
        }
      })
      }


      if (this.showSuggestions && this.suggestions.length > 0) {
        Column({ space: 2 }) {
          ForEach(this.suggestions, (value: string) => {
            Text(value)
              .fontSize(12)
              .fontColor('#CFE0FF')
              .width('100%')
              .padding({ left: 12, right: 12, top: 7, bottom: 7 })
              .backgroundColor('#17171F')
              .maxLines(1)
              .textOverflow({ overflow: TextOverflow.Ellipsis })
              .onClick(() => {
                this.pickSuggestion(value);
              })
          }, (value: string) => value)
        }
        .width('100%')
        .backgroundColor('#12121A')
      }

      if (this.downloadVisible) {
        Row({ space: 8 }) {
          Text(this.downloadText)
            .fontSize(12)
            .fontColor('#CFE3FF')
            .layoutWeight(1)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
          Text('收起')
            .fontSize(12)
            .fontColor('#8FA8CC')
            .onClick(() => {
              this.downloadVisible = false;
            })
        }
        .width('100%')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#182338')
      }

      Stack({ alignContent: Alignment.Center }) {
        GeckoSurface({
          sessionId: this.activeTabId,
          showPlaceholder: false
        })
        if (!this.engineRenderReady) {
          this.placeholderContent()
        }
        if (this.fullscreenUi) {
          Button('退出全屏')
            .fontSize(12)
            .height(30)
            .backgroundColor('#AA1C1C26')
            .fontColor('#E6E6F0')
            .margin({ top: 10 })
            .onClick(() => {
              this.fullscreenUi = false;
              GeckoViewBoot.exitFullscreen();
            })
        }
        if (this.menuVisible) {
          Stack() {
            Column() {
            }
            .width('100%')
            .height('100%')
            .onClick(() => {
              this.closeMenu(true);
            })
            Scroll() {
              Column({ space: 2 }) {
                ForEach(this.menuRows, (row: MenuRow) => {
                  if (row.kind === 'separator') {
                    Divider()
                      .strokeWidth(1)
                      .color('#2A2A3A')
                      .margin({ top: 3, bottom: 3 })
                  } else {
                    Row({ space: 6 }) {
                      Text(row.hasChildren ? (row.expanded ? '▾' : '▸') : (row.checked ? '✓' : ''))
                        .fontSize(12)
                        .fontColor('#7FD18B')
                        .width(14)
                      Text(row.label)
                        .fontSize(13)
                        .fontColor(row.disabled ? '#5A5A6E' : '#E6E6F0')
                        .layoutWeight(1)
                        .maxLines(1)
                        .textOverflow({ overflow: TextOverflow.Ellipsis })
                      if (row.accel.length > 0) {
                        Text(row.accel)
                          .fontSize(10)
                          .fontColor('#6E6E85')
                      }
                    }
                    .width('100%')
                    .padding({ left: 10 + row.depth * 12, right: 10, top: 7, bottom: 7 })
                    .borderRadius(6)
                    .backgroundColor('#242433')
                    .onClick(() => {
                      this.tapMenuRow(row);
                    })
                  }
                }, (row: MenuRow) => `${row.id}|${row.label}|${row.checked}|${row.disabled}`)
              }
              .width('100%')
            }
            .width(260)
            .constraintSize({ maxHeight: 420 })
            .scrollBar(BarState.Off)
            .backgroundColor('#1C1C26')
            .borderRadius(10)
            .padding(6)
            .position({ x: Math.min(this.menuX, 900), y: Math.min(this.menuY, 700) })
          }
          .width('100%')
          .height('100%')
        }

        if (this.loadError.length > 0) {
          Column({ space: 14 }) {
            Text('页面加载失败')
              .fontSize(18)
              .fontWeight(FontWeight.Medium)
              .fontColor('#E6E6F0')
            Text(this.loadError)
              .fontSize(13)
              .fontColor('#A0A0B8')
              .textAlign(TextAlign.Center)
              .maxLines(3)
            Row({ space: 12 }) {
              Button('重试')
                .fontSize(14)
                .backgroundColor('#4C6FFF')
                .fontColor('#FFFFFF')
                .onClick(() => {
                  this.retryLoad();
                })
              Button('回到首页')
                .fontSize(14)
                .backgroundColor('#2A2A3A')
                .fontColor('#E6E6F0')
                .onClick(() => {
                  this.goHome();
                })
            }
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
          .padding(24)
          .backgroundColor('#F2101014')
        }
      }
      .width('100%')
      .onAreaChange((oldArea: Area, newArea: Area) => {
        this.contentWidth = Number(newArea.width);
        this.contentHeight = Number(newArea.height);
      })
      .layoutWeight(1)

      if (this.findVisible) {
        Row({ space: 8 }) {
          TextInput({ text: this.findQuery, placeholder: '页内查找' })
            .fontSize(13)
            .height(34)
            .layoutWeight(1)
            .backgroundColor('#1C1C26')
            .fontColor('#E6E6F0')
            .onChange((value: string) => {
              this.findQuery = value;
            })
            .onSubmit(() => {
              this.findNext(false);
            })
          Button('上一个')
            .fontSize(12)
            .height(34)
            .backgroundColor('#2A2A3A')
            .fontColor('#E6E6F0')
            .onClick(() => {
              this.findNext(true);
            })
          Button('下一个')
            .fontSize(12)
            .height(34)
            .backgroundColor('#2A2A3A')
            .fontColor('#E6E6F0')
            .onClick(() => {
              this.findNext(false);
            })
          Button('关闭')
            .fontSize(12)
            .height(34)
            .backgroundColor('#1C1C26')
            .fontColor('#8A8AA3')
            .onClick(() => {
              this.findVisible = false;
            })
        }
        .width('100%')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#12121A')
      }



      if (this.statusMessage.length > 0) {
        Text(this.statusMessage)
          .fontSize(11)
          .fontColor('#A0A0B8')
          .width('100%')
          .padding({ left: 12, right: 12, top: 4, bottom: 4 })
          .backgroundColor('#12121A')
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
      }

      if (!this.fullscreenUi) {
        Row({ space: 4 }) {
          this.panelButton('书签', PANEL_BOOKMARKS)
          this.panelButton('历史', PANEL_HISTORY)
          this.panelButton('下载', PANEL_DOWNLOADS)
          this.panelButton('设置', PANEL_SETTINGS)
          Button('收藏')
            .fontSize(11)
            .height(26)
            .backgroundColor('#1F2A1F')
            .fontColor('#A8E6B0')
            .borderRadius(6)
            .onClick(() => {
              this.addCurrentBookmark();
            })
          Button(this.privateMode ? '退出私密' : '私密')
            .fontSize(11)
            .height(26)
            .backgroundColor(this.privateMode ? '#2A1F3A' : '#17171F')
            .fontColor(this.privateMode ? '#C9A7FF' : '#A0A0B8')
            .borderRadius(6)
            .onClick(() => {
              this.togglePrivateMode();
            })
          Blank()
          Button(this.findVisible ? '隐藏查找' : '查找')
            .fontSize(11)
            .height(26)
            .backgroundColor('#1C1C26')
            .fontColor('#C8C8DC')
            .borderRadius(6)
            .onClick(() => {
              this.findVisible = !this.findVisible;
            })
          Button('−')
            .fontSize(14)
            .width(30)
            .height(26)
            .padding(0)
            .backgroundColor('#1C1C26')
            .fontColor('#E6E6F0')
            .borderRadius(6)
            .onClick(() => {
              this.zoomBy(-0.1);
            })
          Text(`${Math.round(this.zoomLevel * 100)}%`)
            .fontSize(10)
            .fontColor('#A0A0B8')
            .width(36)
            .textAlign(TextAlign.Center)
          Button('+')
            .fontSize(14)
            .width(30)
            .height(26)
            .padding(0)
            .backgroundColor('#1C1C26')
            .fontColor('#E6E6F0')
            .borderRadius(6)
            .onClick(() => {
              this.zoomBy(0.1);
            })
        }
        .width('100%')
        .padding({ left: 8, right: 8, top: 3, bottom: 3 })
        .backgroundColor('#0E0E12')
      }

      if (!this.fullscreenUi) {
      TabBar({
        tabs: this.tabs,
        activeTabId: this.activeTabId,
        privateMode: this.privateMode,
        onMenu: () => {
          this.openPanel(PANEL_SETTINGS);
        },
        onSelectTab: (tabId: string) => {
          this.viewModel.activateTab(tabId);
          const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
          if (engineIndex !== undefined) {
            GeckoViewBoot.switchToSession(engineIndex);
            this.repaintSoon();
          }
          this.dismissKeyboard();
          this.syncTabs();
        },
        onCloseTab: (tabId: string) => {
          const engineIndex: number | undefined = this.engineIndexOfTab(tabId);
          this.viewModel.closeTab(tabId);
          if (engineIndex !== undefined) {
            GeckoViewBoot.closeSession(engineIndex);
            this.engineIndexByTab.delete(tabId);
            this.tabByEngineIndex.delete(engineIndex);
          }
          const activeIndex: number | undefined = this.activeEngineIndex();
          if (activeIndex !== undefined) {
            GeckoViewBoot.switchToSession(activeIndex);
            this.repaintSoon();
          }
          this.dismissKeyboard();
          this.syncTabs();
        },
        onNewTab: () => {
          const modelUrl: string = TabViewModel.newTabUrl();
          const created = this.viewModel.createTab(modelUrl);
          const engineIndex: number = this.nextEngineIndex++;
          this.bindEngineSession(created.id, engineIndex);
          const engineUrl: string = modelUrl === 'about:newtab' ? 'https://example.org/' : modelUrl;
          this.pushHistory(created.id, engineUrl);
          GeckoViewBoot.createSession(engineIndex, engineUrl);
          GeckoViewBoot.switchToSession(engineIndex);
          this.repaintSoon();
          this.dismissKeyboard();
          this.syncTabs();
        }
      })
      }


      if (this.activePanel === PANEL_BOOKMARKS) {
        Column() {
          BookmarksView({
            bookmarks: this.bookmarks,
            privateMode: this.privateMode,
            onOpen: (url: string) => {
              this.navigate(url);
            },
            onRemove: (id: string) => {
              this.removeBookmark(id);
            },
            onRefresh: () => {
              this.refreshPanels();
            }
          })
        }
        .width('100%')
        .height(300)
        .backgroundColor('#101018')
      } else if (this.activePanel === PANEL_HISTORY) {
        Column() {
          HistoryView({
            entries: this.historyEntries,
            privateMode: this.privateMode,
            onOpen: (url: string) => {
              this.navigate(url);
            },
            onClear: () => {
              this.clearHistory();
            },
            onRefresh: () => {
              this.refreshPanels();
            }
          })
        }
        .width('100%')
        .height(300)
        .backgroundColor('#101018')
      } else if (this.activePanel === PANEL_DOWNLOADS) {
        Column() {
          DownloadsView({
            records: this.downloadRecords,
            privateMode: this.privateMode,
            onCancel: (id: string) => {
              this.cancelDownload(id);
            },
            onRetry: (id: string) => {
              this.retryDownload(id);
            },
            onOpen: (id: string) => {
              this.openDownload(id);
            },
            onClear: () => {
              this.clearDownloads();
            },
            onRefresh: () => {
              this.refreshPanels();
            }
          })
        }
        .width('100%')
        .height(300)
        .backgroundColor('#101018')
      } else if (this.activePanel === PANEL_SETTINGS) {
        Column() {
          SettingsView({
            javascriptEnabled: this.javascriptEnabled,
            imagesEnabled: this.imagesEnabled,
            doNotTrack: this.doNotTrack,
            privateByDefault: this.privateByDefault,
            searchEngine: this.searchEngine,
            accountName: this.accountName,
            engineLabel: this.engineLabel,
            onToggleJavascript: (enabled: boolean) => {
              this.javascriptEnabled = enabled;
              this.settings.setJavascriptEnabled(enabled);
            },
            onToggleImages: (enabled: boolean) => {
              this.imagesEnabled = enabled;
              this.settings.setImagesEnabled(enabled);
            },
            onToggleDoNotTrack: (enabled: boolean) => {
              this.doNotTrack = enabled;
              this.settings.setDoNotTrackEnabled(enabled);
            },
            onTogglePrivateByDefault: (enabled: boolean) => {
              this.privateByDefault = enabled;
              this.settings.setPrivateByDefault(enabled);
            },
            onChangeSearchEngine: (value: string) => {
              this.searchEngine = value;
              this.settings.setSearchEngine(value);
            },
            onExportData: () => {
              this.exportData();
            },
            onImportData: () => {
              this.importData();
            },
            onOpenDiagnostics: () => {
              this.openDiagnostics();
            }
          })
        }
        .width('100%')
        .height(360)
        .backgroundColor('#101018')
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0E0E12')
  }
}

/** Sequenced page-title event published by EntryAbility. */
interface TitleEvent {
  seq: number;
  session: string;
  title: string;
  url: string;
}

interface DownloadEvent {
  type: string;
  id: number;
  url?: string;
  filename?: string;
  totalBytes?: number;
  receivedBytes?: number;
  path?: string;
  errorCode?: string;
}

interface PickerRequest {
  id: number;
  mode: string;
  title?: string;
  mimeTypes?: Array<string>;
  suffixes?: Array<string>;
}

interface PickerEvent {
  id: number;
  req: string;
}

interface MenuAnchor {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface MenuItem {
  kind: string;
  id: number;
  label: string;
  accel: string;
  icon?: string;
  disabled: boolean;
  checked: boolean;
  hidden: boolean;
  items?: Array<MenuItem>;
}

interface MenuPayload {
  menuId: number;
  title?: string;
  anchor?: MenuAnchor;
  point?: boolean;
  items: Array<MenuItem>;
}

class MenuRow {
  kind: string = 'item';
  hasChildren: boolean = false;
  expanded: boolean = false;
  id: number = 0;
  label: string = '';
  accel: string = '';
  disabled: boolean = false;
  checked: boolean = false;
  depth: number = 0;
}
