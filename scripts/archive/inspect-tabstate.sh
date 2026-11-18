#!/bin/bash
set -u
echo "=== tab-state observer (OHOSChromeBridge.cpp 85-165) ==="
sed -n '85,165p' /home/dev/ff/gecko/widget/openharmony/OHOSChromeBridge.cpp
echo
echo "=== RegisterTabStateCallback NAPI ==="
ln=$(grep -n 'napi_value RegisterTabStateCallback' /home/dev/ff/gecko/ports/ohos/geckoview.cpp | head -1 | cut -d: -f1)
sed -n "${ln},$((ln+45))p" /home/dev/ff/gecko/ports/ohos/geckoview.cpp
echo
echo "=== geckoview.js TabOpen/TabAttrModified notify sites ==="
grep -n 'airweb-tab-state' /home/dev/ff/gecko/mobile/shared/chrome/geckoview/geckoview.js | head
