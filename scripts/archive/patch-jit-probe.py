#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add an RWX/JIT capability probe NAPI + let the engine decide JIT itself."""
import io

ROOT = '/mnt/d/ff-ohos/work/firefoxport'

# ------------------------------------------------ gecko_module.cpp: jitProbe
p = ROOT + '/gecko/src/main/cpp/src/gecko_module.cpp'
src = io.open(p, encoding='utf-8').read()

if 'JitProbe' not in src:
    src = src.replace('#include <cstdio>', '#include <cstdio>\n#include <cerrno>\n#include <cstring>\n#include <sys/mman.h>\n#include <unistd.h>', 1)

    anchor = "// ---------------------------------------------------------------------------\n// Module registration\n// ---------------------------------------------------------------------------"
    assert src.count(anchor) == 1
    probe = '''// ---------------------------------------------------------------------------
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
             "{\\"rwx\\":%d,\\"rwxErrno\\":%d,\\"mprotect\\":%d,\\"mprotectErrno\\":%d,"
             "\\"exec\\":%d,\\"pageSize\\":%zu}",
             rwxOk ? 1 : 0, rwxErrno, mprotectOk ? 1 : 0, mprotectErrno,
             execOk ? 1 : 0, page);

    char logBuf[600];
    snprintf(logBuf, sizeof(logBuf), "JIT_PROBE %s", json);
    LogInfo(logBuf);

    napi_value result = nullptr;
    napi_create_string_utf8(env, json, NAPI_AUTO_LENGTH, &result);
    return result;
}

''' + anchor
    src = src.replace(anchor, probe)

    a = '        {"readLogTail", nullptr, ReadLogTail, nullptr, nullptr, nullptr, napi_default, nullptr},'
    assert src.count(a) == 1
    src = src.replace(a, a + '\n        {"jitProbe", nullptr, JitProbe, nullptr, nullptr, nullptr, napi_default, nullptr},')
    io.open(p, 'w', encoding='utf-8').write(src)
print('gecko_module jitProbe ok')

# ------------------------------------------------ gecko_napi.h declaration
p = ROOT + '/gecko/src/main/cpp/include/gecko_napi.h'
src = io.open(p, encoding='utf-8').read()
if 'JitProbe' not in src:
    a = "napi_value ReadLogTail(napi_env env, napi_callback_info info);"
    assert src.count(a) == 1
    src = src.replace(a, a + "\n\n// JIT capability probe (RWX / mprotect / execute).\nnapi_value JitProbe(napi_env env, napi_callback_info info);")
    io.open(p, 'w', encoding='utf-8').write(src)
print('gecko_napi.h ok')

# ------------------------------------------------ d.ts
p = ROOT + '/gecko/src/main/cpp/types/libgecko_napi/index.d.ts'
src = io.open(p, encoding='utf-8').read()
if 'jitProbe' not in src:
    a = "export const readLogTail: (path: string, maxBytes?: number) => string;"
    assert src.count(a) == 1
    src = src.replace(a, a + "\n\n/** JIT capability probe: RWX mmap / mprotect / execute results. */\nexport const jitProbe: () => string;")
    io.open(p, 'w', encoding='utf-8').write(src)
print('d.ts ok')

# ------------------------------------------------ GeckoEngine.ets
p = ROOT + '/gecko/src/main/ets/GeckoEngine.ets'
src = io.open(p, encoding='utf-8').read()
if 'jitProbe' not in src:
    a = "  isJsEngineAvailable,"
    assert src.count(a) == 1
    src = src.replace(a, "  isJsEngineAvailable,\n  jitProbe,")
    a = "  /** M2 diagnostics: tail of a sandbox file (e.g. Gecko NSPR log). */"
    assert src.count(a) == 1
    src = src.replace(a, "  /** JIT capability probe (RWX / mprotect / execute). */\n  static probeJit(): string {\n    return jitProbe();\n  }\n\n" + a)
    io.open(p, 'w', encoding='utf-8').write(src)
print('GeckoEngine ok')

# ------------------------------------------------ GeckoService: run probe + log
p = ROOT + '/entry/src/main/ets/service/GeckoService.ets'
src = io.open(p, encoding='utf-8').read()
if 'probeJit' not in src:
    a = "      hilog.info(DOMAIN, TAG, 'Native bridge initialized');"
    assert src.count(a) == 1
    src = src.replace(a, a + "\n      try {\n        const probe = GeckoEngine.probeJit();\n        hilog.info(DOMAIN, TAG, 'JIT probe: %{public}s', probe);\n      } catch (probeError) {\n        hilog.warn(DOMAIN, TAG, 'JIT probe failed: %{public}s', JSON.stringify(probeError));\n      }")
    io.open(p, 'w', encoding='utf-8').write(src)
print('GeckoService ok')

# ------------------------------------------------ GeckoViewBoot: drop no-jit flag
p = ROOT + '/gecko/src/main/ets/GeckoViewBoot.ets'
src = io.open(p, encoding='utf-8').read()
a = "      commandlineArgs: '--airweb-force-no-jit',"
assert src.count(a) == 1
src = src.replace(a, "      // No --airweb-force-no-jit: XPCOMInit probes RWX mmap and enables the\n      // full JIT backend when the kernel permission is actually available.\n      commandlineArgs: '',")
io.open(p, 'w', encoding='utf-8').write(src)
print('GeckoViewBoot no-jit flag removed')
