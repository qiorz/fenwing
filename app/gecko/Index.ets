/**
 * Public entry point of the `gecko` HSP.
 * Consumers import from 'gecko' only; internal paths stay private.
 */

export { EngineVersionInfo, GeckoEngine, XulSmokeReport } from './src/main/ets/GeckoEngine';
export { GeckoViewBoot, GeckoViewHandlers, SurfaceSizeReport } from './src/main/ets/GeckoViewBoot';
