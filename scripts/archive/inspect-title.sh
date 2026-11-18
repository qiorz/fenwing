#!/bin/bash
set -u
cd /home/dev/ff/gecko/ports/ohos
echo "=== title usages in port ==="
grep -n -i 'title' geckoview.cpp | head -20
echo
echo "=== ChromeJSCall ==="
ln=$(grep -n 'napi_value ChromeJSCall' geckoview.cpp | head -1 | cut -d: -f1)
sed -n "${ln},$((ln+70))p" geckoview.cpp
echo
echo "=== OHOSChromeBridge call impl (libxul side) ==="
grep -n 'GeckoBridge_ChromeJSCall' -A 40 /home/dev/ff/gecko/widget/openharmony/OHOSChromeBridge.cpp | head -70
