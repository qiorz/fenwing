/*
 * SpiderMonkey adapter for evaluateScript (M1), adapted to the actual
 * SpiderMonkey 142 (Firefox 142.0a1) public API shipped by this build.
 *
 * API differences already handled here (vs. the original M0 sketch):
 *  - 142 has no public JS_NewRuntime/JS_DestroyRuntime: JS_NewContext() creates
 *    the context *and* its runtime (see js/Context.h);
 *  - interrupt hooks are JS_AddInterruptCallback / JS_RequestInterruptCallback
 *    (js/Interrupt.h);
 *  - JS_EncodeStringToUTF8 returns a RAII JS::UniqueChars, not a malloc'd ptr;
 *  - every public header requires js-confdefs.h platform defines (XP_UNIX...),
 *    injected via the -include flag in CMakeLists.txt.
 *
 * Threading: JS_NewContext must happen on a single thread; this adapter is only
 * reached from the NAPI (ArkTS) thread and keeps one process-wide context.
 */

#include "gecko_napi.h"

#ifdef GECKO_HAVE_MOZJS

#include <chrono>
#include <cstring>
#include <string>

#include <hilog/log.h>

#include <js/CharacterEncoding.h>
#include <js/Class.h>
#include <js/CompilationAndEvaluation.h>
#include <js/CompileOptions.h>
#include <js/Context.h>
#include <js/Conversions.h>
#include <js/GlobalObject.h>
#include <js/Initialization.h>
#include <js/Interrupt.h>
#include <js/Realm.h>
#include <js/RealmOptions.h>
#include <js/RootingAPI.h>
#include <js/SourceText.h>
#include <js/TypeDecls.h>
#include <js/Utility.h>
#include <jsapi.h>

namespace {

constexpr uint32_t kLogDomain = 0x3203;
constexpr const char* kLogTag = "GeckoMozJS";

// Script budget: small by design (evaluateScript is a debug/test surface).
constexpr uint32_t kRuntimeHeapBytes = 64u * 1024u * 1024u;

JSContext* g_context = nullptr;
JS::PersistentRooted<JSObject*>* g_global = nullptr;
std::chrono::steady_clock::time_point g_deadline;
bool g_interruptArmed = false;

// Minimal global for script evaluation (JS::Evaluate needs a realm).
const JSClass kGlobalClass = {"gecko-global", JSCLASS_GLOBAL_FLAGS,
                              &JS::DefaultGlobalClassOps};

void LogInfo(const char* message) {
    OH_LOG_Print(LOG_APP, LOG_INFO, kLogDomain, kLogTag, "%{public}s", message);
}

void LogError(const char* message) {
    OH_LOG_Print(LOG_APP, LOG_ERROR, kLogDomain, kLogTag, "%{public}s", message);
}

bool InterruptCallback(JSContext* context) {
    (void)context;
    if (!g_interruptArmed) {
        return false;
    }
    return std::chrono::steady_clock::now() > g_deadline;
}

bool EnsureContext() {
    if (g_context != nullptr) {
        return true;
    }
    // JS_Init is idempotent-safe for this process-wide, single-threaded use.
    static bool initialized = false;
    LogInfo("probe: before JS_Init");
    if (!initialized) {
        if (!JS_Init()) {
            LogError("JS_Init failed");
            return false;
        }
        initialized = true;
        LogInfo("probe: JS_Init ok");
    }
    LogInfo("probe: before JS_NewContext");
    g_context = JS_NewContext(kRuntimeHeapBytes);
    if (g_context == nullptr) {
        LogError("JS_NewContext failed");
        return false;
    }
    if (!JS::InitSelfHostedCode(g_context)) {
        LogError("JS::InitSelfHostedCode failed");
        JS_DestroyContext(g_context);
        g_context = nullptr;
        return false;
    }
    LogInfo("probe: InitSelfHostedCode ok");
    LogInfo("probe: before JS_NewGlobalObject");
    // JS::Evaluate requires a current global: create a minimal realm.
    JS::RealmOptions realmOptions;
    JS::RootedObject global(
        g_context, JS_NewGlobalObject(g_context, &kGlobalClass, nullptr,
                                      JS::FireOnNewGlobalHook, realmOptions));
    if (!global) {
        LogError("JS_NewGlobalObject failed");
        JS_DestroyContext(g_context);
        g_context = nullptr;
        return false;
    }
    LogInfo("probe: global created");
    g_global = new JS::PersistentRooted<JSObject*>(g_context, global);
    LogInfo("probe: persistent rooted ok");
    // Interrupt callback disabled for bring-up: test plain evaluation first.
    LogInfo("SpiderMonkey context ready (interpreter-only build)");
    return true;
}

std::string ExceptionText(JSContext* context) {
    JS::RootedValue exception(context);
    if (!JS_GetPendingException(context, &exception)) {
        return "unknown script error";
    }
    JS_ClearPendingException(context);
    JS::RootedString text(context, JS::ToString(context, exception));
    if (!text) {
        return "script error (unprintable exception)";
    }
    JS::UniqueChars utf8 = JS_EncodeStringToUTF8(context, text);
    if (!utf8) {
        return "script error (encoding failed)";
    }
    return std::string(utf8.get());
}

}  // namespace

namespace gecko {

ScriptResult EvaluateWithMozjs(const std::string& script, int32_t timeoutMs) {
    ScriptResult result;
    if (!EnsureContext()) {
        result.error = "SpiderMonkey context unavailable";
        return result;
    }

    g_deadline = std::chrono::steady_clock::now() +
                 std::chrono::milliseconds(timeoutMs > 0 ? timeoutMs : 1000);
    g_interruptArmed = true;
    // JS_RequestInterruptCallback(g_context);

    LogInfo("probe: entering realm");
    JSAutoRealm realm(g_context, g_global->get());
    LogInfo("probe: realm ok");

    JS::CompileOptions options(g_context);
    options.setFileAndLine("gecko-eval.js", 1);

    // SpiderMonkey 142 evaluates from JS::SourceText, not a raw char buffer.
    // Borrowed is safe here: `script` outlives the Evaluate() call below.
    JS::SourceText<mozilla::Utf8Unit> source;
    if (!source.init(g_context, script.c_str(), script.size(),
                     JS::SourceOwnership::Borrowed)) {
        result.error = "failed to allocate the script source buffer";
        return result;
    }

    JS::RootedValue value(g_context);
    LogInfo("probe: before Evaluate");
    const bool evaluated =
        JS::Evaluate(g_context, options, source, &value);
    g_interruptArmed = false;

    if (!evaluated) {
        result.error = ExceptionText(g_context);
        LogError(result.error.c_str());
        return result;
    }

    JS::RootedString text(g_context, JS::ToString(g_context, value));
    if (!text) {
        result.error = "script returned a value that cannot be stringified";
        return result;
    }
    JS::UniqueChars utf8 = JS_EncodeStringToUTF8(g_context, text);
    if (!utf8) {
        result.error = "failed to encode the script result";
        return result;
    }
    result.value.assign(utf8.get());
    result.ok = true;
    return result;
}

}  // namespace gecko

#endif  // GECKO_HAVE_MOZJS



