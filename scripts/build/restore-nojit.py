import io
ROOT='/mnt/d/ff-ohos/work/firefoxport'
# 1) restore force-no-jit flag until ACL is available
p=ROOT+'/gecko/src/main/ets/GeckoViewBoot.ets'
s=io.open(p,encoding='utf-8').read()
a="      // No --airweb-force-no-jit: XPCOMInit probes RWX mmap and enables the\n      // full JIT backend when the kernel permission is actually available.\n      commandlineArgs: '',"
assert s.count(a)==1
s=s.replace(a, "      // JIT requires the restricted kernel permissions (ALLOW_WRITABLE_CODE_MEMORY\n      // etc.) via a signing-profile ACL. Without ACL the page maps RWX but SIGILLs\n      // on execution, so keep the interpreter fallback until the ACL profile exists.\n      commandlineArgs: '--airweb-force-no-jit',")
io.open(p,'w',encoding='utf-8').write(s)
# 2) stop calling the exec probe (it faults on this device); keep NAPI for future
p=ROOT+'/entry/src/main/ets/service/GeckoService.ets'
s=io.open(p,encoding='utf-8').read()
a="""      try {
        const probe = GeckoEngine.probeJit();
        hilog.info(DOMAIN, TAG, 'JIT probe: %{public}s', probe);
      } catch (probeError) {
        hilog.warn(DOMAIN, TAG, 'JIT probe failed: %{public}s', JSON.stringify(probeError));
      }
"""
assert s.count(a)==1
s=s.replace(a,"")
io.open(p,'w',encoding='utf-8').write(s)
print('restored no-jit mode, probe call removed')
