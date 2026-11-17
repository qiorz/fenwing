#!/bin/bash
set -u
cd /home/dev/ff/gecko/ports/ohos
echo "=== session id format (auto-?) ==="
grep -n '"auto-' geckoview.cpp | head -10
grep -n 'auto-%d\|snprintf.*auto' geckoview.cpp | head -10
echo
echo "=== CreateSession body ==="
ln=$(grep -n 'napi_value CreateSession' geckoview.cpp | head -1 | cut -d: -f1)
sed -n "${ln},$((ln+55))p" geckoview.cpp
echo
echo "=== SwitchToSession / FocusWebview ==="
for fn in SwitchToSession FocusWebview DeleteWebview NextWindowId CloseSession; do
  ln=$(grep -n "napi_value $fn" geckoview.cpp | head -1 | cut -d: -f1)
  echo "--- $fn (line $ln) ---"
  [ -n "${ln:-}" ] && sed -n "${ln},$((ln+40))p" geckoview.cpp
done
