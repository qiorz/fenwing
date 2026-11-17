/*
 * Gecko for HarmonyOS - NAPI bridge public header.
 *
 * The NAPI module is the ONLY boundary between ArkTS and the Gecko embedding
 * layer. ArkTS must never depend on Gecko internal C++ types; everything is
 * expressed as primitive values, strings or flat objects.
 *
 * Threading contract:
 *  - every napi_env / napi_value is used on the ArkTS thread that invoked us;
 *  - native -> ArkTS callbacks go through napi_threadsafe_function (M3+);
 *  - no napi_value is stored across calls.
 */

#ifndef GECKO_NAPI_H
#define GECKO_NAPI_H

#include <cstdint>
#include <string>

#include <napi/native_api.h>

namespace gecko {

/**
 * Version / build identity reported by `getVersion`.
 * Values are filled in by the build pipeline (M0 lock step) and default to
 * explicit "not-built" markers so nothing can be mistaken for a real engine.
 */
struct EngineVersion {
    static constexpr const char* kEngineName = "Gecko";
    static constexpr const char* kBuildVersion = "0.1.0-m0";
    static constexpr const char* kFirefoxBaseline = "unpinned-m0";
    static constexpr const char* kTargetAbi = "arm64-v8a";
    static constexpr int32_t kNapiSchemaVersion = 1;
};

/**
 * Error codes shared with ArkTS (`entry/src/main/ets/common/GeckoErrors.ets`).
 * Keep this list and the ArkTS enum in sync; T052 audits the pair.
 */
struct ErrorCode {
    static constexpr const char* kNotInitialized = "NOT_INITIALIZED";
    static constexpr const char* kInvalidSession = "INVALID_SESSION";
    static constexpr const char* kSurfaceError = "SURFACE_ERROR";
    static constexpr const char* kEngineCrash = "ENGINE_CRASH";
    static constexpr const char* kUnsupported = "UNSUPPORTED";
    static constexpr const char* kIoError = "IO_ERROR";
    static constexpr const char* kTimeout = "TIMEOUT";
    static constexpr const char* kPermissionDenied = "PERMISSION_DENIED";
};

/** Bind every exported method onto the NAPI exports object. */
napi_value RegisterGeckoModule(napi_env env, napi_value exports);

/** True when libmozjs.so + jsapi.h were staged at build time (M1). */
bool IsMozjsAvailable();

/** Outcome of a single script evaluation. */
struct ScriptResult {
    bool ok = false;
    std::string value;
    std::string error;
};

/**
 * Evaluates `script` with SpiderMonkey. Implemented in mozjs_eval.cpp, which is
 * only compiled when GECKO_HAVE_MOZJS is defined (see CMakeLists.txt).
 * Single-threaded: caller must be on the NAPI thread.
 */
ScriptResult EvaluateWithMozjs(const std::string& script, int32_t timeoutMs);

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------
napi_value Initialize(napi_env env, napi_callback_info info);
napi_value Shutdown(napi_env env, napi_callback_info info);
napi_value GetVersion(napi_env env, napi_callback_info info);
napi_value Ping(napi_env env, napi_callback_info info);

// ---------------------------------------------------------------------------
// Sessions (M2+; stubs return UNSUPPORTED until the engine is embedded)
// ---------------------------------------------------------------------------
napi_value CreateSession(napi_env env, napi_callback_info info);
napi_value DestroySession(napi_env env, napi_callback_info info);
napi_value LoadUrl(napi_env env, napi_callback_info info);
napi_value GoBack(napi_env env, napi_callback_info info);
napi_value GoForward(napi_env env, napi_callback_info info);
napi_value Reload(napi_env env, napi_callback_info info);
napi_value Stop(napi_env env, napi_callback_info info);
napi_value GetSessionState(napi_env env, napi_callback_info info);
napi_value SetObserver(napi_env env, napi_callback_info info);

// ---------------------------------------------------------------------------
// Surface / input (M3+)
// ---------------------------------------------------------------------------
napi_value AttachSurface(napi_env env, napi_callback_info info);
napi_value DetachSurface(napi_env env, napi_callback_info info);
napi_value ResizeSurface(napi_env env, napi_callback_info info);
napi_value DispatchTouch(napi_env env, napi_callback_info info);
napi_value DispatchKey(napi_env env, napi_callback_info info);
napi_value DispatchWheel(napi_env env, napi_callback_info info);
napi_value DispatchIme(napi_env env, napi_callback_info info);

// ---------------------------------------------------------------------------
// Scripting (M1)
// ---------------------------------------------------------------------------
napi_value EvaluateScript(napi_env env, napi_callback_info info);
napi_value IsJsEngineAvailable(napi_env env, napi_callback_info info);

// ---------------------------------------------------------------------------
// Internal helpers shared with the Rust bridge binding (T022)
// ---------------------------------------------------------------------------
napi_value RustAdd(napi_env env, napi_callback_info info);

// M2 smoke: dlopen libxul.so and call XRE_GetBootstrap inside the app sandbox.
napi_value XulSmoke(napi_env env, napi_callback_info info);

// M2 diagnostics: read the tail of a sandbox text file (Gecko NSPR log) so the
// ArkTS layer can surface it through hilog when the shell user cannot read it.
napi_value ReadLogTail(napi_env env, napi_callback_info info);

// JIT capability probe (RWX / mprotect / execute).
napi_value JitProbe(napi_env env, napi_callback_info info);

}  // namespace gecko

#endif  // GECKO_NAPI_H
