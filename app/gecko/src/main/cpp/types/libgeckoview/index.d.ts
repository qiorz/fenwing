/**
 * Type declarations for libgeckoview.so (community OHOS Gecko embedding NAPI).
 * Minimal surface used by the M2/M3 bring-up; extend as milestones land.
 */

export interface GeckoViewInitOptions {
  url?: string;
  resourceDir?: string;
  commandlineArgs?: string;
  uiMode?: string;
}

export interface SurfaceSize {
  width: number;
  height: number;
}

export const initFirefox: (options: GeckoViewInitOptions) => void;
export const loadURL: (url: string) => void;

// Multi-session (tab) management. sessionId == numeric browserIndex; the
// initial engine browser created at startup uses index 0.
export const createSession: (sessionId: number, url?: string) => void;
export const switchToSession: (sessionId: number) => void;
export const closeSession: (sessionId: number) => void;
export const loadURLForSession: (sessionId: number, url: string) => void;
export const forceRepaint: () => void;

// Per-session navigation / history.
export const goBackForSession: (sessionId: number) => void;
export const goForwardForSession: (sessionId: number) => void;
export const reloadForSession: (sessionId: number) => void;
export const stopForSession: (sessionId: number) => void;
export const getSessionHistory: () => { index: number; count: number };
export const goBack: () => void;
export const goForward: () => void;
export const reload: () => void;
export const stop: () => void;
export const registerURLcallback: (callback: (sessionId: string, url: string) => void) => void;
export const registerPageLoadCallback: (callback: (sessionId: string, state: string) => void) => void;
export const registerProgressCallback: (callback: (progress: number) => void) => void;
export const registerTabStateCallback: (callback: (json: string) => void) => void;
export const registerMenuCallback: (callback: (json: string) => void) => void;
export const resolveMenuCommand: (menuId: number, itemId: number, modifiers: number) => void;
export const closeNativeMenu: (menuId: number) => void;
export const registerDownloadCallback: (callback: (json: string) => void) => void;
export const registerFilePickerCallback: (callback: (json: string, callbackId: number) => void) => void;
export const registerFullscreenCallback: (callback: (fullscreen: boolean) => void) => void;
export const resolveFilePicker: (callbackId: number, result: number, path: string) => void;
export const exitFullscreen: () => void;
export const findInPage: (query: string, backward: number, matchCase: number) => void;
export const setFullZoom: (zoom: number) => void;
export const registerFirstCompositeCallback: (callback: () => void) => void;
export const registerTerminateCallback: (callback: () => void) => void;
export const registerPromptToastCallback: (callback: (message: string) => void) => void;
export const registerIMECallback: (callback: (state: string) => void) => void;
export const getSurfaceSize: () => SurfaceSize;
export const setBoolPref: (name: string, value: number) => void;
export const setCharPref: (name: string, value: string) => void;

// Input forwarding (coordinates are in Gecko surface pixels).
export const touchEvent: (action: number, x: number, y: number, time: number) => void;
export const mouseMove: (x: number, y: number) => void;
export const mouseDown: (x: number, y: number, button: number) => void;
export const mouseUp: (x: number, y: number, button: number) => void;
export const scroll: (dx: number, dy: number, x: number, y: number) => void;
export const dispatchKeyEvent: (action: number, keyCode: number, modifiers?: number) => void;

// IME text bridge (ArkTS TextInput -> Gecko).
export const insertText: (text: string) => void;
export const deleteText: (length: number) => void;
