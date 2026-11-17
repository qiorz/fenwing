/**
 * GeckoService - entry-side facade over the `gecko` HSP.
 *
 * Responsibilities:
 *  - own the engine lifecycle (initialize once, release on ability destroy);
 *  - translate native errors into GeckoError;
 *  - expose a stable, UI-friendly API (version summary, smoke probe, evaluate);
 *  - degrade explicitly instead of silently: every unimplemented engine
 *    capability returns UNSUPPORTED until its milestone is gated in.
 */

import { EngineVersionInfo, GeckoEngine } from 'gecko';
import { hilog } from '@kit.PerformanceAnalysisKit';
import {
  EngineAvailability,
  EngineProbeResult,
  EngineVersionSummary,
  SessionConfig
} from '../common/GeckoTypes';
import { GeckoError, GeckoErrorCode, toGeckoError } from '../common/GeckoErrors';

const DOMAIN: number = 0x3201;
const TAG: string = 'GeckoService';

export class GeckoService {
  private static instance: GeckoService | undefined = undefined;

  private initialized: boolean = false;
  private lastError: GeckoError | undefined = undefined;
  private versionCache: EngineVersionSummary | undefined = undefined;

  static getInstance(): GeckoService {
    if (GeckoService.instance === undefined) {
      GeckoService.instance = new GeckoService();
    }
    return GeckoService.instance;
  }

  /** Initializes the native bridge. Returns false when loading failed. */
  async initialize(): Promise<boolean> {
    if (this.initialized) {
      return true;
    }
    try {
      await GeckoEngine.ensureInitialized();
      this.initialized = true;
      this.lastError = undefined;
      this.versionCache = undefined;
      hilog.info(DOMAIN, TAG, 'Native bridge initialized');
      // NOTE: do NOT call GeckoEngine.xulLoadSmoke() here. XRE_GetBootstrap is
      // a one-shot API (MOZ_RELEASE_ASSERT on second call), and the real engine
      // boot (libgeckoview InitFirefox) owns that single call. The NAPI smoke
      // entry stays available for manual diagnostics only.
      return true;
    } catch (error) {
      const geckoError = toGeckoError(error as Object);
      this.lastError = geckoError;
      this.initialized = false;
      hilog.error(DOMAIN, TAG, 'Native bridge failed: %{public}s', geckoError.detail);
      return false;
    }
  }

  /** Releases the native bridge; call from EntryAbility.onDestroy. */
  async release(): Promise<void> {
    if (!this.initialized) {
      return;
    }
    try {
      await GeckoEngine.release();
      hilog.info(DOMAIN, TAG, 'Native bridge released');
    } catch (error) {
      const geckoError = toGeckoError(error as Object);
      hilog.warn(DOMAIN, TAG, 'Release failed: %{public}s', geckoError.detail);
    } finally {
      this.initialized = false;
      this.versionCache = undefined;
    }
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  getLastError(): GeckoError | undefined {
    return this.lastError;
  }

  /** Version summary for the UI; never throws (returns UNKNOWN on failure). */
  getVersionSummary(): EngineVersionSummary {
    if (this.versionCache !== undefined) {
      return this.versionCache;
    }
    const summary = new EngineVersionSummary();
    try {
      const info: EngineVersionInfo = GeckoEngine.getVersionInfo();
      summary.engine = info.engine;
      summary.geckoVersion = info.geckoVersion;
      summary.buildId = info.buildId;
      summary.abi = info.abi;
      summary.jsEngine = info.jsEngine;
      summary.rustBridge = info.rustBridge;
      summary.rustBridgeAbi = info.rustBridgeAbi;
      summary.napiSchemaVersion = info.napiSchemaVersion;
      summary.initialized = info.initialized;
      summary.availability = GeckoService.resolveAvailability(info);
    } catch (error) {
      const geckoError = toGeckoError(error as Object);
      this.lastError = geckoError;
      summary.availability = EngineAvailability.UNAVAILABLE;
    }
    this.versionCache = summary;
    return summary;
  }

  /** ArkTS -> NAPI round trip. Throws GeckoError on failure. */
  ping(message: string): string {
    try {
      return GeckoEngine.ping(message);
    } catch (error) {
      throw toGeckoError(error as Object);
    }
  }

  /** True when libmozjs.so is staged (M1). */
  hasJsEngine(): boolean {
    try {
      return GeckoEngine.hasJsEngine();
    } catch (error) {
      return false;
    }
  }

  /**
   * ArkTS -> NAPI -> Rust smoke probe used by the M0 debug page.
   * Failures are collected in the result instead of thrown so the UI can
   * render a partial report.
   */
  async probe(): Promise<EngineProbeResult> {
    const result = new EngineProbeResult();
    result.startedAt = Date.now();
    const ready: boolean = await this.initialize();
    if (!ready) {
      result.errors.push('initialize failed: native bridge unavailable');
      result.finishedAt = Date.now();
      return result;
    }
    try {
      result.pingReply = this.ping('m0-smoke');
    } catch (error) {
      const geckoError = toGeckoError(error as Object);
      result.errors.push(`ping failed: ${geckoError.detail}`);
    }
    result.rustAddLeft = 21;
    result.rustAddRight = 21;
    try {
      result.rustAddResult = GeckoEngine.add(result.rustAddLeft, result.rustAddRight);
      result.rustBridgeOk = result.rustAddResult === 42;
      if (!result.rustBridgeOk) {
        result.errors.push(`rustAdd returned ${result.rustAddResult}, expected 42`);
      }
    } catch (error) {
      const geckoError = toGeckoError(error as Object);
      result.rustBridgeOk = false;
      result.errors.push(`rustAdd failed: ${geckoError.detail}`);
    }
    result.jsEngineAvailable = this.hasJsEngine();
    result.ok = result.pingReply.length > 0 && result.rustBridgeOk && result.errors.length === 0;
    result.finishedAt = Date.now();
    return result;
  }

  /**
   * Evaluates a script through the native bridge. Rejects with UNSUPPORTED when
   * libmozjs.so is not staged.
   */
  async evaluate(script: string, timeoutMs: number): Promise<string> {
    try {
      return await GeckoEngine.evaluate(script, timeoutMs);
    } catch (error) {
      throw toGeckoError(error as Object);
    }
  }

  /**
   * Session entry point. The embedding layer is gated behind M2, so this
   * always reports UNSUPPORTED with an actionable message.
   */
  createSession(config: SessionConfig): void {
    throw new GeckoError(
      GeckoErrorCode.UNSUPPORTED,
      `createSession is not available yet (profile=${config.profileId}); the Gecko embedding layer lands in M2.`,
      'M2-gated'
    );
  }

  private static resolveAvailability(info: EngineVersionInfo): EngineAvailability {
    if (!info.initialized) {
      return EngineAvailability.UNAVAILABLE;
    }
    if (info.jsEngine === 'libmozjs') {
      return EngineAvailability.JS_ONLY;
    }
    return EngineAvailability.BRIDGE_ONLY;
  }
}
