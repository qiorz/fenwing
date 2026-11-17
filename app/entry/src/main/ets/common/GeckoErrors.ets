/**
 * Error model shared by the entry module.
 *
 * Native error codes originate in gecko/src/main/cpp/include/gecko_napi.h.
 * Keep both lists in sync; the Polish task T052 audits the pair.
 */

import { BusinessError } from '@kit.BasicServicesKit';

/**
 * hilog domain map (keep in sync with the native side):
 *   0x3201 NAPI bridge / GeckoService      (gecko_module.cpp)
 *   0x3202 XComponent surface              (GeckoSurface.ets)
 *   0x3203 SpiderMonkey / JS smoke         (mozjs_eval.cpp, JsSmokePage.ets)
 *   0x3204 local account / import-export   (LocalAccountService.ets)
 *   0x3205 browser UI shell                (BrowserPage.ets)
 */
export class GeckoLogDomain {
  static readonly NAPI: number = 0x3201;
  static readonly SURFACE: number = 0x3202;
  static readonly JS: number = 0x3203;
  static readonly ACCOUNT: number = 0x3204;
  static readonly UI: number = 0x3205;
}

export enum GeckoErrorCode {
  NOT_INITIALIZED = 'NOT_INITIALIZED',
  INVALID_SESSION = 'INVALID_SESSION',
  SURFACE_ERROR = 'SURFACE_ERROR',
  ENGINE_CRASH = 'ENGINE_CRASH',
  UNSUPPORTED = 'UNSUPPORTED',
  IO_ERROR = 'IO_ERROR',
  TIMEOUT = 'TIMEOUT',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  UNKNOWN = 'UNKNOWN'
}

export class GeckoError extends Error {
  code: GeckoErrorCode = GeckoErrorCode.UNKNOWN;
  detail: string = '';

  constructor(code: GeckoErrorCode, message: string, detail: string) {
    super(message);
    this.name = 'GeckoError';
    this.code = code;
    this.detail = detail;
  }

  /** True when the engine capability is intentionally not built yet. */
  isUnsupported(): boolean {
    return this.code === GeckoErrorCode.UNSUPPORTED;
  }
}

/**
 * Human-readable description used by the UI; never throws.
 * Values mirror gecko/src/main/cpp/include/gecko_napi.h ErrorCode.
 */
export function mapNativeCode(raw: string): GeckoErrorCode {
  switch (raw) {
    case 'NOT_INITIALIZED':
      return GeckoErrorCode.NOT_INITIALIZED;
    case 'INVALID_SESSION':
      return GeckoErrorCode.INVALID_SESSION;
    case 'SURFACE_ERROR':
      return GeckoErrorCode.SURFACE_ERROR;
    case 'ENGINE_CRASH':
      return GeckoErrorCode.ENGINE_CRASH;
    case 'UNSUPPORTED':
      return GeckoErrorCode.UNSUPPORTED;
    case 'IO_ERROR':
      return GeckoErrorCode.IO_ERROR;
    case 'TIMEOUT':
      return GeckoErrorCode.TIMEOUT;
    case 'PERMISSION_DENIED':
      return GeckoErrorCode.PERMISSION_DENIED;
    default:
      return GeckoErrorCode.UNKNOWN;
  }
}

/** One-line description for status bars. */
export function describeCode(code: GeckoErrorCode): string {
  switch (code) {
    case GeckoErrorCode.NOT_INITIALIZED:
      return '原生桥未初始化';
    case GeckoErrorCode.INVALID_SESSION:
      return '会话无效';
    case GeckoErrorCode.SURFACE_ERROR:
      return '渲染表面错误';
    case GeckoErrorCode.ENGINE_CRASH:
      return '引擎崩溃或脚本异常';
    case GeckoErrorCode.UNSUPPORTED:
      return '当前里程碑尚未支持';
    case GeckoErrorCode.IO_ERROR:
      return '文件读写失败';
    case GeckoErrorCode.TIMEOUT:
      return '操作超时';
    case GeckoErrorCode.PERMISSION_DENIED:
      return '权限被拒绝';
    default:
      return '未知错误';
  }
}

/** Normalizes anything thrown by NAPI / ArkTS into a GeckoError. */
export function toGeckoError(error: Object): GeckoError {
  if (error instanceof GeckoError) {
    return error;
  }
  const businessError = error as BusinessError;
  const rawCode: string = `${businessError.code}`;
  const message: string = `${businessError.message}`;
  const code: GeckoErrorCode = mapNativeCode(rawCode);
  const detail: string = rawCode === 'undefined' ? message : `${rawCode}: ${message}`;
  return new GeckoError(code, message, detail);
}
