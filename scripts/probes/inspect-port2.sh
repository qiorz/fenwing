#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== geckoview.cpp: permission / ACL / crash ==="
grep -n -i 'ALLOW_WRITABLE_CODE_MEMORY\|ALLOW_EXECUTABLE\|permission\|ACL\|MOZ_CRASH' ports/ohos/geckoview.cpp | head -40
echo
echo "=== NAPI methods registered ==="
grep -n 'DECLARE_NAPI_FUNCTION\|napi_property_descriptor\|static napi_value' ports/ohos/geckoview.cpp | head -50
echo
echo "=== libxul.symbols GeckoBridge ==="
if [ -f toolkit/library/libxul.symbols ]; then
  echo "count: $(grep -c 'GeckoBridge_' toolkit/library/libxul.symbols)"
  grep 'GeckoBridge_' toolkit/library/libxul.symbols | head -30
else
  echo "no libxul.symbols"
fi
echo
echo "=== ports/ohos files ==="
ls -la ports/ohos/
echo
echo "=== permission.json ==="
cat ports/ohos/permission.json
