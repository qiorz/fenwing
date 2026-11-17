/*
 * Gecko for HarmonyOS - NAPI bridge implementation.
 *
 * M0 scope: module registration, version/ping, lifecycle and honest
 * "not yet implemented" errors for the engine-facing surface. Every session,
 * surface and input entry point fails with UNSUPPORTED until the corresponding
 * milestone (M2/M3) is gated in; nothing here pretends to render or navigate.
 */

#include "gecko_napi.h"

#include <cstdio>
#include <cerrno>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>
#include <string>
#include <vector>

#include <dlfcn.h>
#include <hilog/log.h>

// M0 Rust smoke bridge (gecko/rust/ohos-smoke). Linked only when staged.
#ifdef GECKO_HAVE_RUST_SMOKE
extern "C" int32_t ohos_rust_add(int32_t left, int32_t right);
extern "C" uint32_t ohos_rust_bridge_version(void);
#endif

namespace {

constexpr uint32_t kLogDomain = 0x3201;
constexpr const char* kLogTag = "GeckoNAPI";

bool g_bridgeInitialized = false;

void LogInfo(const char* message) {
    OH_LOG_Print(LOG_APP, LOG_INFO, kLogDomain, kLogTag, "%{public}s", message);
}

void LogError(const char* message) {
    OH_LOG_Print(LOG_APP, LOG_ERROR, kLogDomain, kLogTag, "%{public}s", message);
}

napi_value Undefined(napi_env env) {
    napi_value value = nullptr;
    napi_get_undefined(env, &value);
    return value;
}

template <size_t N>
size_t ReadNapiString(napi_env env, napi_value value, char (&buf)[N]) {
    size_t len = 0;
    if (napi_get_value_string_utf8(env, value, buf, N, &len) != napi_ok) {
        return 0;
    }
    buf[N - 1] = '\0';
    return len;
}

napi_value MakeString(napi_env env, const char* text) {
    napi_value value = nullptr;
    napi_create_string_utf8(env, text, NAPI_AUTO_LENGTH, &value);
    return value;
}

napi_value MakeInt32(napi_env env, int32_t number) {
    napi_value value = nullptr;
    napi_create_int32(env, number, &value);
    return value;
}

napi_value MakeBoolean(napi_env env, bool flag) {
    napi_value value = nullptr;
    napi_get_boolean(env, flag, &value);
    return value;
}

napi_value ResolvedVoidPromise(napi_env env) {
    napi_deferred deferred = nullptr;
    napi_value promise = nullptr;
    napi_create_promise(env, &deferred, &promise);
    napi_resolve_deferred(env, deferred, Undefined(env));
    return promise;
}

napi_value RejectedPromise(napi_env env, const char* code, const char* message) {
    LogError((std::string(code) + ": " + message).c_str());
    napi_deferred deferred = nullptr;
    napi_value promise = nullptr;
    napi_create_promise(env, &deferred, &promise);

    napi_value codeValue = MakeString(env, code);
    napi_value messageValue = MakeString(env, message);
    napi_value error = nullptr;
    napi_create_error(env, codeValue, messageValue, &error);
    napi_reject_deferred(env, deferred, error);
    return promise;
}

/** Read one UTF-8 string argument; returns false when the value is not a string. */
bool GetStringArg(napi_env env, napi_value value, std::string& out) {
    napi_valuetype type = napi_undefined;
    if (napi_typeof(env, value, &type) != napi_ok || type != napi_string) {
        return false;
    }
    size_t length = 0;
    if (napi_get_value_string_utf8(env, value, nullptr, 0, &length) != napi_ok) {
        return false;
    }
    std::vector<char> buffer(length + 1, '\0');
    if (napi_get_value_string_utf8(env, value, buffer.data(), buffer.size(), &length) != napi_ok) {
        return false;
    }
    out.assign(buffer.data(), length);
    return true;
}

/**
 * Single place that logs + throws a coded error. Keeping this centralised is
 * what T052 audits: every native rejection must carry one of ErrorCode's
 * values and appear in hilog with the method name.
 */
napi_value ThrowCoded(napi_env env, const char* code, const char* method, const char* detail) {
    std::string message = std::string(method) + ": " + detail + " [" + code + "]";
    LogError(message.c_str());
    napi_throw_error(env, code, message.c_str());
    return nullptr;
}

napi_value ThrowUnsupported(napi_env env, const char* method) {
    return ThrowCoded(env, gecko::ErrorCode::kUnsupported, method,
                      "not available in the M0 bridge; the Gecko embedding layer is gated behind milestone M2");
}

}  // namespace

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

napi_value gecko::Initialize(napi_env env, napi_callback_info info) {
    (void)info;
    if (g_bridgeInitialized) {
        LogInfo("initialize: NAPI bridge already initialized (idempotent)");
        return ResolvedVoidPromise(env);
    }
    g_bridgeInitialized = true;
#ifdef GECKO_HAVE_MOZJS
    LogInfo("initialize: NAPI bridge ready (libmozjs staged, M1 scope)");
    {
        // One-shot JS self-test: proves libmozjs.so can be loaded and evaluated
        // inside the HarmonyOS app sandbox without touching the UI.
        const gecko::ScriptResult probe = gecko::EvaluateWithMozjs("21+21", 2000);
        std::string msg = std::string("MOZJS_SELFTEST ok=") + (probe.ok ? "1" : "0") +
                          " value=" + probe.value + " error=" + probe.error;
        LogInfo(msg.c_str());
    }
#else
    LogInfo("initialize: NAPI bridge ready (engine not embedded, M0 scope)");
#endif
    return ResolvedVoidPromise(env);
}

napi_value gecko::Shutdown(napi_env env, napi_callback_info info) {
    (void)info;
    if (!g_bridgeInitialized) {
        return ResolvedVoidPromise(env);
    }
    g_bridgeInitialized = false;
    LogInfo("shutdown: NAPI bridge released");
    return ResolvedVoidPromise(env);
}

napi_value gecko::GetVersion(napi_env env, napi_callback_info info) {
    (void)info;
    napi_value result = nullptr;
    napi_create_object(env, &result);
    napi_set_named_property(env, result, "engine", MakeString(env, EngineVersion::kEngineName));
    napi_set_named_property(env, result, "geckoVersion", MakeString(env, EngineVersion::kFirefoxBaseline));
    napi_set_named_property(env, result, "buildId", MakeString(env, EngineVersion::kBuildVersion));
    napi_set_named_property(env, result, "abi", MakeString(env, EngineVersion::kTargetAbi));
    napi_set_named_property(env, result, "napiSchemaVersion", MakeInt32(env, EngineVersion::kNapiSchemaVersion));
    napi_set_named_property(env, result, "jsEngine", MakeString(env, IsMozjsAvailable() ? "libmozjs" : "unavailable"));
#ifdef GECKO_HAVE_RUST_SMOKE
    napi_set_named_property(env, result, "rustBridge", MakeString(env, "libohos_smoke"));
    napi_set_named_property(env, result, "rustBridgeAbi", MakeInt32(env, static_cast<int32_t>(ohos_rust_bridge_version())));
#else
    napi_set_named_property(env, result, "rustBridge", MakeString(env, "unavailable"));
    napi_set_named_property(env, result, "rustBridgeAbi", MakeInt32(env, 0));
#endif
    napi_set_named_property(env, result, "initialized", MakeBoolean(env, g_bridgeInitialized));
    return result;
}

napi_value gecko::Ping(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1] = {nullptr};
    napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);

    std::string payload = "ping";
    if (argc > 0) {
        std::string argument;
        if (GetStringArg(env, argv[0], argument)) {
            payload = argument;
        }
    }
    std::string reply = "pong: " + payload;
    LogInfo(reply.c_str());
    return MakeString(env, reply.c_str());
}

// ---------------------------------------------------------------------------
// Sessions - engine not embedded yet (M2)
// ---------------------------------------------------------------------------

napi_value gecko::CreateSession(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "createSession");
}

napi_value gecko::DestroySession(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "destroySession");
}

napi_value gecko::LoadUrl(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "loadUrl");
}

napi_value gecko::GoBack(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "goBack");
}

napi_value gecko::GoForward(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "goForward");
}

napi_value gecko::Reload(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "reload");
}

napi_value gecko::Stop(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "stop");
}

napi_value gecko::GetSessionState(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "getSessionState");
}

napi_value gecko::SetObserver(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "setObserver");
}

// ---------------------------------------------------------------------------
// Surface / input - M3
// ---------------------------------------------------------------------------

napi_value gecko::AttachSurface(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "attachSurface");
}

napi_value gecko::DetachSurface(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "detachSurface");
}

napi_value gecko::ResizeSurface(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "resizeSurface");
}

napi_value gecko::DispatchTouch(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "dispatchTouch");
}

napi_value gecko::DispatchKey(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "dispatchKey");
}

napi_value gecko::DispatchWheel(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "dispatchWheel");
}

napi_value gecko::DispatchIme(napi_env env, napi_callback_info info) {
    (void)info;
    return ThrowUnsupported(env, "dispatchIme");
}

// ---------------------------------------------------------------------------
// Scripting - M1
// ---------------------------------------------------------------------------

napi_value gecko::EvaluateScript(napi_env env, napi_callback_info info) {
    size_t argc = 2;
    napi_value argv[2] = {nullptr, nullptr};
    napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);

    std::string script;
    if (argc < 1 || !GetStringArg(env, argv[0], script)) {
        return RejectedPromise(env, ErrorCode::kInvalidSession,
                               "evaluateScript expects (script: string, timeoutMs?: number)");
    }

    int32_t timeoutMs = 1000;
    if (argc > 1) {
        int32_t requested = 0;
        if (napi_get_value_int32(env, argv[1], &requested) == napi_ok && requested > 0) {
            timeoutMs = requested;
        }
    }

#ifdef GECKO_HAVE_MOZJS
    const ScriptResult evalResult = EvaluateWithMozjs(script, timeoutMs);
    if (!evalResult.ok) {
        return RejectedPromise(env, ErrorCode::kEngineCrash, evalResult.error.c_str());
    }
    napi_deferred deferred = nullptr;
    napi_value promise = nullptr;
    napi_create_promise(env, &deferred, &promise);
    napi_resolve_deferred(env, deferred, MakeString(env, evalResult.value.c_str()));
    return promise;
#else
    (void)timeoutMs;
    return RejectedPromise(env, ErrorCode::kUnsupported,
                           "evaluateScript is unavailable: libmozjs.so was not staged (see m1-report.md).");
#endif
}

bool gecko::IsMozjsAvailable() {
#ifdef GECKO_HAVE_MOZJS
    return true;
#else
    return false;
#endif
}

napi_value gecko::IsJsEngineAvailable(napi_env env, napi_callback_info info) {
    (void)info;
    return MakeBoolean(env, IsMozjsAvailable());
}

// ---------------------------------------------------------------------------
// Rust bridge (M0)
// ---------------------------------------------------------------------------

napi_value gecko::RustAdd(napi_env env, napi_callback_info info) {
#ifdef GECKO_HAVE_RUST_SMOKE
    size_t argc = 2;
    napi_value argv[2] = {nullptr, nullptr};
    napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);
    if (argc < 2) {
        return ThrowCoded(env, ErrorCode::kInvalidSession, "rustAdd", "expects (left: number, right: number)");
        return nullptr;
    }
    int32_t left = 0;
    int32_t right = 0;
    if (napi_get_value_int32(env, argv[0], &left) != napi_ok ||
        napi_get_value_int32(env, argv[1], &right) != napi_ok) {
        return ThrowCoded(env, ErrorCode::kInvalidSession, "rustAdd", "arguments must be 32-bit integers");
        return nullptr;
    }
    napi_value result = nullptr;
    napi_create_int32(env, static_cast<int32_t>(ohos_rust_add(left, right)), &result);
    return result;
#else
    (void)info;
    return ThrowCoded(env, ErrorCode::kUnsupported, "rustAdd",
                      "libohos_smoke.so was not staged (run scripts/build_rust_smoke.sh)");
    return nullptr;
#endif
}

// ---------------------------------------------------------------------------
// M2 smoke: load libxul.so in the app sandbox and call XRE_GetBootstrap.
// This proves the 185 MB engine shared library (and its NSS/NSPR deps) can be
// dlopen'ed and entered from inside a HarmonyOS HAP/HSP process.
// ---------------------------------------------------------------------------
napi_value gecko::XulSmoke(napi_env env, napi_callback_info info) {
    (void)info;
    napi_value result = nullptr;
    napi_create_object(env, &result);

    auto setBool = [&](const char* name, bool value) {
        napi_value v; napi_get_boolean(env, value, &v);
        napi_set_named_property(env, result, name, v);
    };
    auto setStr = [&](const char* name, const std::string& value) {
        napi_value v; napi_create_string_utf8(env, value.c_str(), value.size(), &v);
        napi_set_named_property(env, result, name, v);
    };

    void* handle = dlopen("libxul.so", RTLD_NOW | RTLD_GLOBAL);
    if (handle == nullptr) {
        const char* err = dlerror();
        setBool("dlopenOk", false);
        setStr("error", err ? err : "dlopen failed");
        LogError((std::string("XUL_SMOKE dlopen failed: ") + (err ? err : "?")).c_str());
        return result;
    }
    setBool("dlopenOk", true);
    setStr("error", "");

    void* sym = dlsym(handle, "XRE_GetBootstrap");
    setBool("symbolOk", sym != nullptr);
    if (sym == nullptr) {
        LogError("XUL_SMOKE XRE_GetBootstrap symbol missing");
        return result;
    }

    // ABI note: mozilla::Bootstrap::UniquePtr is one pointer + stateless
    // deleter, and XRE_GetBootstrap takes it by reference; passing void*& is
    // ABI-compatible for this side-effect-only smoke call.
    using GetBootstrapFn = void (*)(void*&);
    void* bootstrap = nullptr;
    reinterpret_cast<GetBootstrapFn>(sym)(bootstrap);
    setBool("bootstrapOk", bootstrap != nullptr);
    setStr("bootstrap", bootstrap ? "non-null" : "null");

    std::string msg = std::string("XUL_SMOKE dlopen=1 symbol=1 bootstrap=") +
                      (bootstrap ? "non-null" : "null");
    LogInfo(msg.c_str());
    return result;
}

// ---------------------------------------------------------------------------
// M2 diagnostics: return the tail of a sandbox file (e.g. gecko_nspr.txt).
// ---------------------------------------------------------------------------
napi_value gecko::ReadLogTail(napi_env env, napi_callback_info info) {
    size_t argc = 2;
    napi_value argv[2] = {nullptr, nullptr};
    napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);
    if (argc < 1) {
        return ThrowCoded(env, ErrorCode::kIoError, "readLogTail", "expects (path: string, maxBytes?: number)");
    }
    char pathBuf[1024] = {0};
    if (ReadNapiString(env, argv[0], pathBuf) == 0) {
        return ThrowCoded(env, ErrorCode::kIoError, "readLogTail", "path must be a string");
    }
    int32_t maxBytes = 8192;
    if (argc >= 2) {
        napi_get_value_int32(env, argv[1], &maxBytes);
    }
    if (maxBytes <= 0 || maxBytes > 65536) {
        maxBytes = 8192;
    }

    napi_value result = nullptr;
    FILE* fp = fopen(pathBuf, "rb");
    if (fp == nullptr) {
        napi_create_string_utf8(env, "", 0, &result);
        return result;
    }
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    long start = size > maxBytes ? size - maxBytes : 0;
    fseek(fp, start, SEEK_SET);
    std::string out;
    out.resize(static_cast<size_t>(size - start));
    size_t got = fread(&out[0], 1, out.size(), fp);
    out.resize(got);
    fclose(fp);
    napi_create_string_utf8(env, out.c_str(), out.size(), &result);
    return result;
}

// ---------------------------------------------------------------------------
// JIT capability probe: can this app map/execute writable code memory?
// HarmonyOS gates RWX on the restricted kernel permissions
// (ALLOW_WRITABLE_CODE_MEMORY etc.) which must be granted via the signing
// profile ACL. This probe reports the ground truth from the device.
// ---------------------------------------------------------------------------
napi_value gecko::JitProbe(napi_env env, napi_callback_info info) {
    (void)info;
    const long pageSize = sysconf(_SC_PAGESIZE);
    const size_t page = pageSize > 0 ? static_cast<size_t>(pageSize) : 4096;

    bool rwxOk = false;
    bool mprotectOk = false;
    bool execOk = false;
    int rwxErrno = 0;
    int mprotectErrno = 0;

    // AArch64: mov w0, #7 ; ret
    const uint32_t code[2] = {0x528000E0u, 0xD65F03C0u};

    void* p = mmap(nullptr, page, PROT_READ | PROT_WRITE | PROT_EXEC,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) {
        rwxErrno = errno;
    } else {
        rwxOk = true;
        std::memcpy(p, code, sizeof(code));
        auto fn = reinterpret_cast<int (*)()>(p);
        execOk = (fn() == 7);
        munmap(p, page);
    }

    if (!rwxOk) {
        void* q = mmap(nullptr, page, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (q != MAP_FAILED) {
            std::memcpy(q, code, sizeof(code));
            if (mprotect(q, page, PROT_READ | PROT_EXEC) == 0) {
                mprotectOk = true;
                auto fn = reinterpret_cast<int (*)()>(q);
                execOk = (fn() == 7);
            } else {
                mprotectErrno = errno;
            }
            munmap(q, page);
        } else {
            mprotectErrno = errno;
        }
    }

    char json[512];
    snprintf(json, sizeof(json),
             "{\"rwx\":%d,\"rwxErrno\":%d,\"mprotect\":%d,\"mprotectErrno\":%d,"
             "\"exec\":%d,\"pageSize\":%zu}",
             rwxOk ? 1 : 0, rwxErrno, mprotectOk ? 1 : 0, mprotectErrno,
             execOk ? 1 : 0, page);

    char logBuf[600];
    snprintf(logBuf, sizeof(logBuf), "JIT_PROBE %s", json);
    LogInfo(logBuf);

    napi_value result = nullptr;
    napi_create_string_utf8(env, json, NAPI_AUTO_LENGTH, &result);
    return result;
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

napi_value gecko::RegisterGeckoModule(napi_env env, napi_value exports) {
    napi_property_descriptor properties[] = {
        {"initialize", nullptr, Initialize, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"shutdown", nullptr, Shutdown, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"getVersion", nullptr, GetVersion, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"ping", nullptr, Ping, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"createSession", nullptr, CreateSession, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"destroySession", nullptr, DestroySession, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"loadUrl", nullptr, LoadUrl, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"goBack", nullptr, GoBack, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"goForward", nullptr, GoForward, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"reload", nullptr, Reload, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"stop", nullptr, Stop, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"getSessionState", nullptr, GetSessionState, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"setObserver", nullptr, SetObserver, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"attachSurface", nullptr, AttachSurface, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"detachSurface", nullptr, DetachSurface, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"resizeSurface", nullptr, ResizeSurface, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"dispatchTouch", nullptr, DispatchTouch, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"dispatchKey", nullptr, DispatchKey, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"dispatchWheel", nullptr, DispatchWheel, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"dispatchIme", nullptr, DispatchIme, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"evaluateScript", nullptr, EvaluateScript, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"isJsEngineAvailable", nullptr, IsJsEngineAvailable, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"rustAdd", nullptr, RustAdd, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"xulSmoke", nullptr, XulSmoke, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"readLogTail", nullptr, ReadLogTail, nullptr, nullptr, nullptr, napi_default, nullptr},
        {"jitProbe", nullptr, JitProbe, nullptr, nullptr, nullptr, napi_default, nullptr},
    };

    const size_t count = sizeof(properties) / sizeof(properties[0]);
    napi_define_properties(env, exports, count, properties);
    LogInfo("RegisterGeckoModule: NAPI exports bound");
    return exports;
}

namespace {

napi_value Init(napi_env env, napi_value exports) {
    return gecko::RegisterGeckoModule(env, exports);
}

napi_module g_geckoModule = {
    1,          // nm_version
    0,          // nm_flags
    nullptr,    // nm_filename
    Init,       // nm_register_func
    "gecko",    // nm_modname
    nullptr,    // nm_priv
    {nullptr, nullptr, nullptr, nullptr},  // reserved
};

}  // namespace

extern "C" __attribute__((constructor)) void RegisterGeckoNapiModule(void) {
    napi_module_register(&g_geckoModule);
}

