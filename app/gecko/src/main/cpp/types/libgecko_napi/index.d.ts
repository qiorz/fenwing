/**
 * Type declarations for libgecko_napi.so (Gecko for HarmonyOS NAPI bridge).
 * Keep in sync with gecko/src/main/cpp/include/gecko_napi.h.
 */

export interface EngineVersion {
  /** Engine family name. */
  engine: string;
  /** Firefox/Gecko baseline pinned at M0, or an explicit "not built" marker. */
  geckoVersion: string;
  /** This bridge's build identity. */
  buildId: string;
  /** Target ABI of the packaged native libraries. */
  abi: string;
  /** NAPI contract schema version. */
  napiSchemaVersion: number;
  /** "libmozjs" when a JS engine is available, otherwise "unavailable". */
  jsEngine: string;
  /** "libohos_smoke" when the M0 Rust cdylib is linked, otherwise "unavailable". */
  rustBridge: string;
  /** ABI version reported by the Rust bridge (0 when absent). */
  rustBridgeAbi: number;
  /** Whether initialize() completed for this process. */
  initialized: boolean;
}

export interface SessionOptions {
  profileId: string;
  isPrivate: boolean;
  viewportWidth: number;
  viewportHeight: number;
}

export interface SessionState {
  sessionId: string;
  url: string;
  title: string;
  loading: boolean;
  crashed: boolean;
}

export const initialize: (configJson?: string) => Promise<void>;
export const shutdown: () => Promise<void>;
export const getVersion: () => EngineVersion;
export const ping: (message: string) => string;

export const createSession: (options: SessionOptions) => string;
export const destroySession: (sessionId: string) => void;
export const loadUrl: (sessionId: string, url: string) => void;
export const goBack: (sessionId: string) => void;
export const goForward: (sessionId: string) => void;
export const reload: (sessionId: string) => void;
export const stop: (sessionId: string) => void;
export const getSessionState: (sessionId: string) => SessionState;
export const setObserver: (observerId: string) => void;

export const attachSurface: (sessionId: string, surfaceId: string, width: number, height: number, density: number) => void;
export const detachSurface: (sessionId: string) => void;
export const resizeSurface: (sessionId: string, width: number, height: number) => void;
export const dispatchTouch: (sessionId: string, eventJson: string) => void;
export const dispatchKey: (sessionId: string, eventJson: string) => void;
export const dispatchWheel: (sessionId: string, eventJson: string) => void;
export const dispatchIme: (sessionId: string, eventJson: string) => void;

export const evaluateScript: (script: string, timeoutMs?: number) => Promise<string>;
export const isJsEngineAvailable: () => boolean;

export const rustAdd: (a: number, b: number) => number;

/** M2 smoke: dlopen libxul.so + XRE_GetBootstrap inside the app sandbox. */
export interface XulSmokeReport {
  dlopenOk: boolean;
  symbolOk: boolean;
  bootstrapOk: boolean;
  bootstrap: string;
  error: string;
}
export const xulSmoke: () => XulSmokeReport;

/** M2 diagnostics: tail of a sandbox file (Gecko NSPR/MOZ log). */
export const readLogTail: (path: string, maxBytes?: number) => string;

/** JIT capability probe: RWX mmap / mprotect / execute results. */
export const jitProbe: () => string;
export const codecProbe: () => string;
