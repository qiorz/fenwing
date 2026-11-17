#!/bin/bash
set -u
CFG=/mnt/c/Users/Lenovo/.ohos/config
echo "=== materials (latest first) ==="
ls -lt "$CFG" | head -20
echo
for P in "$CFG"/*.p7b; do
  [ -f "$P" ] || continue
  OUT=$(mktemp)
  if openssl cms -verify -inform DER -in "$P" -noverify -out "$OUT" 2>/dev/null; then
    python3 - "$OUT" "$P" <<'PY'
import json,sys
out,p=sys.argv[1],sys.argv[2]
try:
    d=json.load(open(out))
except Exception as e:
    print(p,'parse fail',e); raise SystemExit
acls=(d.get('acls') or {}).get('allowed-acls') or []
perms=list((d.get('permissions') or {}).keys())
print(f"{p.split('/')[-1]}: type={d.get('type')} bundle={((d.get('bundle-info') or {}).get('bundle-name'))}")
print(f"  acls={acls}")
print(f"  permissions={perms[:10]}{'...' if len(perms)>10 else ''}")
PY
  else
    echo "$P: cms extract failed"
  fi
  rm -f "$OUT"
done
