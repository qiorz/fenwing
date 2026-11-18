#!/bin/bash
set -u
cd /home/dev/ff/gecko
echo "=== find TabManager in tree ==="
grep -rln 'OHOS_TabManager\|tabManager\|TabManager' mobile/ohos toolkit/components 2>/dev/null | head -10
echo
echo "=== geckoview.js candidates ==="
ls mobile/ohos/chrome/content/ 2>/dev/null | head
find mobile/ohos -name '*.js' -path '*chrome*' 2>/dev/null | head -20
echo
echo "=== CallTabManager impl in libxul ==="
grep -rn 'GeckoBridge_CallTabManager' --include=*.cpp --include=*.h . 2>/dev/null | head -10
