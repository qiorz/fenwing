#!/bin/bash
set -u
cd /home/dev/ff/gecko/ports/ohos
echo "=== CallJsWithString ==="
grep -n 'CallJsWithString' geckoview.cpp | head -5
ln=$(grep -n 'static void CallJsWithString' geckoview.cpp | head -1 | cut -d: -f1)
[ -n "${ln:-}" ] && sed -n "${ln},$((ln+60))p" geckoview.cpp
echo
echo "=== OHOS_IMENotify ==="
ln=$(grep -n 'OHOS_IMENotify' geckoview.cpp | head -1 | cut -d: -f1)
[ -n "${ln:-}" ] && sed -n "${ln},$((ln+40))p" geckoview.cpp
echo
echo "=== RegisterPageLoadCallback / RegisterURLCallback / RegisterProgressCallback bodies ==="
for fn in RegisterURLCallback RegisterPageLoadCallback RegisterProgressCallback; do
  ln=$(grep -n "napi_value $fn" geckoview.cpp | head -1 | cut -d: -f1)
  echo "--- $fn ---"
  [ -n "${ln:-}" ] && sed -n "${ln},$((ln+35))p" geckoview.cpp
done
