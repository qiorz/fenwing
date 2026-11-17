/**
 * Plain data types exchanged between the gecko HSP facade, GeckoService and
 * the UI. No ArkUI state decorators here: these are transport/model objects.
 */

/** How far the native engine has progressed in this build. */
export enum EngineAvailability {
  UNKNOWN = 'UNKNOWN',
  /** Native bridge loaded and answering, engine not embedded (M0). */
  BRIDGE_ONLY = 'BRIDGE_ONLY',
  /** SpiderMonkey available, JS evaluation possible (M1). */
  JS_ONLY = 'JS_ONLY',
  /** Gecko embedding layer usable (M2+). */
  READY = 'READY',
  /** Native module failed to load. */
  UNAVAILABLE = 'UNAVAILABLE'
}

/** UI-facing summary of EngineVersion. */
export class EngineVersionSummary {
  engine: string = '';
  geckoVersion: string = '';
  buildId: string = '';
  abi: string = '';
  jsEngine: string = '';
  rustBridge: string = '';
  rustBridgeAbi: number = 0;
  napiSchemaVersion: number = 0;
  initialized: boolean = false;
  availability: EngineAvailability = EngineAvailability.UNKNOWN;
}

/** Result of the ArkTS -> NAPI -> (Rust / JS) smoke probe. */
export class EngineProbeResult {
  ok: boolean = false;
  pingReply: string = '';
  rustAddLeft: number = 0;
  rustAddRight: number = 0;
  rustAddResult: number = 0;
  rustBridgeOk: boolean = false;
  jsEngineAvailable: boolean = false;
  errors: Array<string> = [];
  startedAt: number = 0;
  finishedAt: number = 0;

  elapsedMs(): number {
    return this.finishedAt - this.startedAt;
  }
}

/** Session creation parameters (mirrors the NAPI contract). */
export class SessionConfig {
  profileId: string = 'default';
  isPrivate: boolean = false;
  viewportWidth: number = 1280;
  viewportHeight: number = 800;
}

/** XComponent surface metrics forwarded to attachSurface (M3). */
export class SurfaceMetrics {
  surfaceId: string = '';
  width: number = 0;
  height: number = 0;
  density: number = 1;
}

/** Engine lifecycle event names used by observers. */
export enum EngineEventKind {
  TITLE_CHANGE = 'onTitleChange',
  URL_CHANGE = 'onUrlChange',
  LOAD_START = 'onLoadStart',
  LOAD_END = 'onLoadEnd',
  PROGRESS = 'onProgress',
  CRASH = 'onCrash',
  RENDER_READY = 'onRenderReady'
}
