#!/bin/bash
set -u
P=/mnt/c/Users/Lenovo/.ohos/config/default_firefoxport_P5ERyG1nXjPmHv2CBaASRK25brrcJ6GDNdgelQKd5o8=.p7b
ls -l "$P"
echo "=== try openssl cms extract ==="
openssl cms -verify -inform DER -in "$P" -noverify -out /tmp/profile.json 2>/dev/null && echo extracted || echo "cms extract failed"
if [ -f /tmp/profile.json ]; then
  head -c 4000 /tmp/profile.json; echo
  echo "=== ACL-ish keys ==="
  grep -o '"[a-zA-Z-]*acl[a-zA-Z-]*"' /tmp/profile.json | sort -u | head
  grep -o 'ALLOW_WRITABLE_CODE_MEMORY\|DISABLE_CODE_MEMORY_PROTECTION\|INHERIT_PARENT_PERMISSION' /tmp/profile.json | sort -u
  echo "=== app-privilege-capabilities ==="
  python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/profile.json'))
except Exception as e:
    print('json parse failed', e)
    raise SystemExit
def walk(o, prefix=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if 'acl' in k.lower() or 'privilege' in k.lower() or 'permission' in k.lower() or 'debug' in k.lower() or 'device' in k.lower():
                print(prefix + k, '=', json.dumps(v, ensure_ascii=False)[:600])
            walk(v, prefix + k + '.')
    elif isinstance(o, list):
        for i, v in enumerate(o[:8]):
            walk(v, prefix + f'[{i}].')
walk(d)
PY
fi
