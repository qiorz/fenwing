import io, shutil
ROOT='/mnt/d/ff-ohos/work/firefoxport'
# declare kernel permissions (needed for DevEco auto-signing to apply for ACL)
p=ROOT+'/entry/src/main/module.json5'
s=io.open(p,encoding='utf-8').read()
if 'ALLOW_WRITABLE_CODE_MEMORY' not in s:
    a='''    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      }
    ],'''
    assert s.count(a)==1
    s=s.replace(a, '''    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.kernel.ALLOW_WRITABLE_CODE_MEMORY"
      },
      {
        "name": "ohos.permission.kernel.DISABLE_CODE_MEMORY_PROTECTION"
      }
    ],''')
    io.open(p,'w',encoding='utf-8').write(s)
print('module.json5 kernel perms declared')
# stage libxul with .permission section; keep interpreter flag for now (crash-safe)
shutil.copyfile('/mnt/d/ff-ohos/artifacts/gecko/libxul-jit.so', ROOT+'/gecko/libs/arm64-v8a/libxul.so')
print('staged libxul.so with .permission; interpreter flag still ON until ACL')
