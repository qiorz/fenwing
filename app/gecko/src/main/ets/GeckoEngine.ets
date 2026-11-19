/**
 * ArkTS facade over libgecko_napi.so.
 *
 * This is the ONLY file in the HSP that talks to the native bridge, so the
 * rest of the app can depend on a small, typed surface. Errors coming from
 * NAPI carry an `error.code` (see gecko/src/main/cpp/include/gecko_napi.h);
 * the entry layer maps them to its own GeckoError type.
 */

import {
  evaluateScript,
  getVersion,
  initialize,
  isJsEngineAvailable,
  codecProbe,
  jitProbe,
  ping,
  readLogTail,
  rustAdd,
  shutdown,
  xulSmoke
} from 'libgecko_napi.so';

/** Plain mirror of the native EngineVersion payload. */
export class EngineVersionInfo {
  engine: string = '';
  geckoVersion: string = '';
  buildId: string = '';
  abi: string = '';
  napiSchemaVersion: number = 0;
  jsEngine: string = '';
  rustBridge: string = '';
  rustBridgeAbi: number = 0;
  initialized: boolean = false;
}

/** Engine lifecycle + diagnostics. Sessions land in M2. */
export class GeckoEngine {
  /** Video decoders reported by OH_AVCodec (JSON array string). */
  static codecProbe(): string {
    try {
      return codecProbe();
    } catch (error) {
      return '[]';
    }
  }

  private static bridgeInitialized: boolean = false;

  /**
   * Initializes the native bridge once per process. Idempotent on both sides:
   * the native side ignores repeated calls.
   */
  static async ensureInitialized(): Promise<void> {
    if (GeckoEngine.bridgeInitialized) {
      return;
    }
    await initialize();
    GeckoEngine.bridgeInitialized = true;
  }

  /** Releases the native bridge. Safe to call when not initialized. */
  static async release(): Promise<void> {
    if (!GeckoEngine.bridgeInitialized) {
      return;
    }
    await shutdown();
    GeckoEngine.bridgeInitialized = false;
  }

  /** Returns the engine/build identity reported by the native bridge. */
  static getVersionInfo(): EngineVersionInfo {
    const raw = getVersion();
    const info = new EngineVersionInfo();
    info.engine = raw.engine;
    info.geckoVersion = raw.geckoVersion;
    info.buildId = raw.buildId;
    info.abi = raw.abi;
    info.napiSchemaVersion = raw.napiSchemaVersion;
    info.jsEngine = raw.jsEngine;
    info.rustBridge = raw.rustBridge;
    info.rustBridgeAbi = raw.rustBridgeAbi;
    info.initialized = raw.initialized;
    return info;
  }

  /** Round-trip smoke check: ArkTS -> NAPI. */
  static ping(message: string): string {
    return ping(message);
  }

  /** M0 smoke check: ArkTS -> NAPI -> Rust cdylib. */
  static add(left: number, right: number): number {
    return rustAdd(left, right);
  }

  /** True when libmozjs.so was staged and the JS engine can be used (M1). */
  static hasJsEngine(): boolean {
    return isJsEngineAvailable();
  }

  /**
   * Evaluates a script on the native side. Rejects with code UNSUPPORTED when
   * libmozjs.so is not staged.
   */
  static async evaluate(script: string, timeoutMs: number): Promise<string> {
    return await evaluateScript(script, timeoutMs);
  }

  /**
   * M2 smoke: loads libxul.so and calls XRE_GetBootstrap inside the app
   * sandbox. Returns the native report object (dlopen/symbol/bootstrap status).
   */
  /** JIT capability probe (RWX / mprotect / execute). */
  static probeJit(): string {
    return jitProbe();
  }

  /** M2 diagnostics: tail of a sandbox file (e.g. Gecko NSPR log). */
  static readLogTail(path: string, maxBytes: number): string {
    return readLogTail(path, maxBytes);
  }
}

/** Native payload of xulSmoke(). */
export class XulSmokeReport {
  dlopenOk: boolean = false;
  symbolOk: boolean = false;
  bootstrapOk: boolean = false;
  bootstrap: string = '';
  error: string = '';
}
