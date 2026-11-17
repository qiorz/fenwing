#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== GeckoBridge_ForceRepaint impl ==="
grep -rn 'GeckoBridge_ForceRepaint' --include=*.cpp . | head -5
ln=$(grep -rn 'void GeckoBridge_ForceRepaint' -l --include=*.cpp . | head -1)
echo "file: $ln"
[ -n "${ln:-}" ] && grep -n 'GeckoBridge_ForceRepaint' -A 40 "$ln" | head -80
echo
echo "=== ResizeSurface NAPI (geckoview.cpp) ==="
ln2=$(grep -n 'napi_value ResizeSurface' ports/ohos/geckoview.cpp | head -1 | cut -d: -f1)
sed -n "${ln2},$((ln2+40))p" ports/ohos/geckoview.cpp
echo
echo "=== attach site context (geckoview.js line ~300) ==="
sed -n '280,330p' mobile/shared/chrome/geckoview/geckoview.js
