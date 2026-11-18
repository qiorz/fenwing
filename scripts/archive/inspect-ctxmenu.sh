#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== ShowContextMenu call sites ==="
grep -rn 'OHOSMenuBridge_ShowContextMenu\|OHOSMenuBridge_Show(' --include=*.cpp --include=*.h . | head -10
echo
echo "=== gating in OHOSMenuBridge.cpp (device/2in1) ==="
grep -n 'tablet\|2in1\|IsPhone\|deviceType\|GetDeviceType\|OHOS_Is' widget/openharmony/OHOSMenuBridge.cpp | head -20
echo
echo "=== ShowMenu hook in nsXULPopupManager ==="
grep -rn 'OHOSMenuBridge' layout/xul/nsXULPopupManager.cpp | head -10
echo
echo "=== geckoview.js contextmenu handling ==="
grep -rn 'contextmenu\|ContextMenu' mobile/shared/chrome/geckoview/geckoview.js | head -20
echo
echo "=== mobile chrome ContextMenu files ==="
find mobile -iname '*contextmenu*' -o -iname '*ContextMenu*' 2>/dev/null | head -20
